# SPDX-FileCopyrightText: 2023-present Remco Boerma <remco.b@educationwarehouse.nl>
#
# SPDX-License-Identifier: MIT
import typing
import uuid
from typing import Optional

from gluon import URL, current, redirect
from gluon.html import DIV, SPAN, TAG, XML, A
from gluon.sqlhtml import SQLFORM
from pydal import DAL
from pydal.objects import Field, Query, Table


def hide(field: Field):
    """Sets a field to be not readable or writable, returns the field for chaining."""
    field.readable = False
    field.writable = False
    return field


def is_uuid(value: str) -> bool:
    """
    Returns whether 'value' is a valid uuid
    """
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def get_actual_column_type(field: Field) -> str | None:
    """
    Execute a raw SQL query to get the column type from PostgreSQL's information schema
    """
    database = field._db

    table_name = field._table._rname
    field_name = field._rname.strip('"')

    # works on tables only:
    # row = database.executesql(
    #     """
    #     SELECT data_type
    #     FROM information_schema.columns
    #     WHERE table_name = %s AND column_name = %s;
    # """,
    #     (table_name, field_name),
    #     colnames=["data_type"],
    # ).first()

    # works on tables and mat. views:
    row = database.executesql(
        """
           SELECT
               CASE
                   WHEN c.relkind IN ('r', 'v', 'm') THEN format_type(a.atttypid, a.atttypmod)
                   ELSE 'unknown'
               END AS data_type
           FROM pg_attribute a
           JOIN pg_class c ON a.attrelid = c.oid
           JOIN pg_namespace n ON c.relnamespace = n.oid
           WHERE (c.relkind = 'r' OR c.relkind = 'v' OR c.relkind = 'm')
           AND c.relname = %s
           AND a.attname = %s
           -- AND n.nspname = 'public'
           ;
       """,
        (table_name, field_name),
        colnames=["data_type"],
    ).first()

    # Return the data type
    return getattr(row, "data_type", None)


def get_actual_column_types(fields: list[Field]) -> dict[Field, str | None]:
    """
    Execute a raw SQL query to get the column types from PostgreSQL's pg_catalog
    """

    # Extract database object from the first field
    if fields:
        database = fields[0]._db
    else:
        return {}

    # Collect table and field names
    table_names = [field._table._rname for field in fields]
    field_names = [field._rname.strip('"') for field in fields]

    # Construct query to get column types for all fields
    query = """
        SELECT
            c.relname AS table_name,
            a.attname AS column_name,
            CASE
                WHEN c.relkind IN ('r', 'v', 'm') THEN format_type(a.atttypid, a.atttypmod)
                ELSE 'unknown'
            END AS data_type
        FROM pg_attribute a
        JOIN pg_class c ON a.attrelid = c.oid
        JOIN pg_namespace n ON c.relnamespace = n.oid
        WHERE (c.relkind = 'r' OR c.relkind = 'v' OR c.relkind = 'm')
        AND c.relname IN %s
        AND a.attname IN %s
    """

    # Execute the query
    rows = database.executesql(query, (tuple(table_names), tuple(field_names)), as_dict=True)

    # Create a dictionary to store the results
    result_dict = {(row["table_name"], row["column_name"]): row["data_type"] for row in rows}

    # Prepare a dictionary with field names and their data types
    field_types = {}
    for field in fields:
        table_name = field._table._rname
        field_name = field._rname.strip('"')
        field_types[field] = result_dict.get((table_name, field_name), None)

    return field_types


def custom_searchable(sfields: list[Field], keywords: str) -> Query:
    filtered_sfields = []
    uuid_sfields = []

    column_types = get_actual_column_types(sfields)

    for field in sfields:
        column_type = column_types.get(field)
        if column_type is None:
            # missing field, skip in search
            continue
        elif column_type == "uuid":
            uuid_sfields.append(field)
        else:
            filtered_sfields.append(field)

    query = SQLFORM.build_query(filtered_sfields, keywords)
    if is_uuid(keywords):
        # uuid only works with exact match, not contains.
        for field in uuid_sfields:
            query |= field == keywords

    return query


class EffectiveDatedTable(Table):
    """
    An effective dated table should have at least these columns:
    """

    id: Field
    effdt: Field
    effstatus: Field
    prio: Field


def effective_dated_grid(
    table: EffectiveDatedTable, keyfieldname: str = "key", query: Optional[Query] = None, use_prio: bool = False, **kwp
):
    """This function creates an effective dated grid, which allows for multiple rows with the same key, but only
    one active row per key. The active row is the one with the latest effective date <= now. The grid allows for
    creating new rows, editing existing rows, and deleting rows.

    Deleting a row will create a new row with the
    same key, but with an effective date of today and an effstatus of False. This will mark the row inactive,
    but will not remove it from the database.

    The grid will also show all rows with an effstatus of False,
    but will not allow for editing or deleting them.

    kwp can be used to pass in any of the parameters used by SQLFORM.grid, with the exception of
    deletable, editable, and create. These are set by the function.

    When using use_prio, the grid will only show the rows with the highest priority for each key,
    and the max effective date <= now and effstatus = True. (so the most recent row within the highest priority)
    """
    # setup()
    db: DAL
    # read parameters
    request = current.request
    auth = current.globalenv["auth"]
    show_archive = bool(request.args and request.args[0] == "archive")
    show_all = bool(request.args and request.args[0] == "all")
    on_delete = bool(request.args and request.args[0] == "ondelete")
    # show_clean = len(request.args) == 0

    kwp.setdefault("searchable", custom_searchable)

    # clean the optional 'archive_fields' key from kwp
    archive_fields = kwp.pop("archive_fields") if "archive_fields" in kwp else []
    if not archive_fields:
        # if no archive_fields are given, use all fields
        # and add the effdt and effstatus fields
        fields = kwp.get("fields", [])
        if "effdt" not in str(fields):
            fields.insert(0, table.effdt)
        if "effstatus" not in str(fields):
            fields.insert(1, table.effstatus)

    # set the args to ignore for the grid
    if show_archive or show_all:
        edg_args = request.args[:1]
    else:
        edg_args = []
    # make sure all required columns are there
    for column in [keyfieldname, "effdt", "effstatus", "id"]:
        if column not in table._fields:
            raise KeyError(f"{column} column not found in {table}.")

    if on_delete:
        # handles the ondelete call generated from a delete button push on the grid
        values = table[request.args[1]].as_dict()
        del values["id"]
        values["effdt"] = request.now
        values["effstatus"] = False
        table.insert(**values)
        redirect(URL())

    if show_all:
        # if the user wants to see the archive, just show the grid
        # the grid will show all rows, but will not allow for editing or deleting them.
        kwp.pop("fields", None)
        kwp.pop("create", None)
        kwp.pop("editable", None)
        kwp.pop("deletable", None)
        kwp.pop("user_signature", None)
        kwp.pop("left", None)  # if tag is coming from kwp, it will ruin our query because of a carthesian product
        grid = SQLFORM.grid(
            table,
            # fields=archive_fields,
            deletable=False,
            editable=False,
            create=False,
            args=edg_args,
            # **kwp,
            user_signature=False,
        )
    else:
        # create the effective dated query
        # start with the with query given by the developer, or default ot a simple one
        query = query if query else (table.id > 0)
        # next apply the effective dated subquery
        d_ed = table.with_alias("d_ed")

        # get the database connection from the table object:
        db = table._db
        # this subquery will return the max(effdt) for each key bound to the outer query
        # based on d_ed.key == table.key. The outer_scoped=[str(table)] is required to
        # make sure the outer query is bound to the subquery.
        if use_prio != False:
            # use prio here
            key_prio_alias = table.with_alias("key_prio")
            key_prio_effdt_alias = table.with_alias("key_prio_effdt")
            key_prio_combination = table[keyfieldname] + "." + table.prio
            key_prio_effdt_combination = table[keyfieldname] + "." + table.prio + "." + table.effdt
            key_prio_subselect = key_prio_combination.belongs(
                db(key_prio_alias[keyfieldname] == table[keyfieldname])._select(
                    key_prio_alias[keyfieldname] + "." + key_prio_alias.prio.max(),
                    groupby=key_prio_alias[keyfieldname],
                    outer_scoped=[str(table)],
                )
            )
            key_prio_effdt_subselect = key_prio_effdt_combination.belongs(
                db(
                    (key_prio_effdt_alias.effdt <= request.now)
                    & (key_prio_effdt_alias[keyfieldname] == table[keyfieldname])
                )._select(
                    key_prio_effdt_alias[keyfieldname]
                    + "."
                    + key_prio_effdt_alias.prio
                    + "."
                    + key_prio_effdt_alias.effdt.max(),
                    groupby=[
                        key_prio_effdt_alias[keyfieldname],
                        key_prio_effdt_alias.prio,
                    ],
                    outer_scoped=[str(table)],
                )
            )
            query &= key_prio_subselect
            query &= key_prio_effdt_subselect
        else:
            # not using prio
            subselect = db((d_ed.effdt <= request.now) & (d_ed[keyfieldname] == table[keyfieldname]))._select(
                d_ed.effdt.max(), outer_scoped=[str(table)]
            )
            query &= table.effdt.belongs(subselect)
        # and in this case, make sure only active rows are visible
        query &= table.effstatus == True
        parent_onvalidation: typing.Callable[[typing.Any], None] | None = kwp.pop("onvalidation", None)

        def onvalidation(form):
            # this is the onvalidation routine that will be called when the user pushes the
            # create or edit button on the grid.

            if parent_onvalidation:
                # if the user applied an onvalidation routine, call it first
                parent_onvalidation(form)
            # figure out what command triggered the onvalidation from within the grid
            # the command is either "new" or "edit" and is the second argument in the
            # request.args list if the archive is being shown, or the first argument if
            # the archive is not being shown.
            edit_cmd = request.args[1] if show_archive else request.args[0]
            if edit_cmd == "new":
                # on create, make sure the key is unique and not copied.
                if db(table[keyfieldname] == form.vars[keyfieldname].strip()).count() > 0:
                    form.errors[keyfieldname] = "Key is already in use."
            elif edit_cmd == "edit":
                # on edit, create a copy of the current row, remove the id field because
                # it will be repopulated for the new row, apply the current effective date
                # and insert the row. The redirect(URL()) will reload the page, showing the new data
                # without the regular grid handling the edit.
                values = table[request.args[-1]].as_dict()
                values.update(form.vars)
                del values["id"]
                values["effdt"] = request.now
                if use_prio is not False:
                    values["prio"] = use_prio
                if "sync_gid" in values:
                    # if a sync_gid column exists, it should be populated with a new gid for
                    # every row to allow syncing between multiple sources.
                    values["sync_gid"] = uuid.uuid4()
                if "last_saved_by" in values:
                    values["last_saved_by"] = auth.user.email
                if "last_saved_when" in values:
                    values["last_saved_when"] = request.now

                if not form.errors:
                    table.insert(**values)
                    return redirect(URL())

        def delete_button(idx):
            # since no onvalidation routine is called on delete, we have to write our own handler and button for it.
            # here's the button.
            return A(
                SPAN(_class="icon trash icon-trash glyphicon glyphicon-trash"),
                XML("&nbsp;"),
                SPAN("Delete", _class="buttontext button"),
                _href=URL(args=["ondelete", idx]),
                _class="button btn btn-default btn-secondary",
            )

        # add the delete link, and any links the user might have added
        links = [{"header": "Delete", "body": lambda row: delete_button(row.id)}, *kwp.pop("links", [])]

        # create the grid with our own onvalidation routine, and the delete button
        # and the links the user might have added. the args are used to pass the
        # show_archive parameter to the grid. all kwp are passed on to the grid.
        grid = SQLFORM.grid(
            db(query),
            onvalidation=onvalidation,  # force our own onvalidation handler, which call any given onvalidation routines
            deletable=False,  # don't use the builtin delete funcitonality
            links=links,  # add the delete button
            args=edg_args,
            user_signature=False,
            **kwp,  # any user given options
        )
        # show sql statement and timing
        # print(db._lastsql[0])
        # print(db._lastsql[1])

    # define the args that will be passed to the button below
    if not request.args:
        # if no args are given, show all from the table
        button_args = ["all"]
    elif request.args[0] in ("all", "archive"):
        # remove the 'all' or 'archive' from the args to toggle between the two
        button_args = request.args[1:]
    else:
        # in every other case add the 'archive' to the args to show the archive
        # for edit or view screens
        button_args = ["archive", *request.args]

    # add a button to toggle between the archive and the active data
    archive_button = A(
        SPAN(_class="icon clock icon-clock glyphicon glyphicon-clock"),
        XML("&nbsp;"),
        SPAN(
            "Hide Archive" if show_all or show_archive else "Show Archive",
            _class="buttontext button",
        ),
        _href=URL(args=button_args),
        # skip our arg when showing archive or append it when not showing active
        _class="button btn btn-default btn-secondary",
    )

    # if show_archive is true, show a table with the change history for the current record
    if show_archive:
        keyfield = getattr(table, keyfieldname)
        current_record = table[request.args[-1]]
        htable = db(keyfield == current_record[keyfieldname]).select(*archive_fields, orderby=~table.effdt)
        # filter out the fields that have different values
        changed_fields = [field for field in archive_fields if len({row[field] for row in htable}) > 1]
        htable = db(keyfield == current_record[keyfieldname]).select(*changed_fields, orderby=~table.effdt)
        # convert the table to a serverside dom queryable XML object
        htable = TAG(htable.xml().decode("utf-8"))

        # stript the `organisation.` from the table headers and replace them with the
        # label from the table definition
        for th in htable.elements("th"):
            th[0] = th[0].replace(b"organisation.", b"")
            th[0] = table[th[0].decode("utf-8")].label

        # color the cells that have a different value than the cell below
        rows = htable.elements("tr")
        if len(rows) > 1:
            for row_idx, row in enumerate(rows[:-1]):
                if row[0][0] == str(request.args[-1]).encode():
                    row["_style"] = "background-color: #ccccff"
                for col_idx, col in enumerate(row.elements("td")[1:], start=1):
                    if str(rows[row_idx][col_idx]) != str(rows[row_idx + 1][col_idx]):
                        col["_style"] = "background-color: #ffcccc"
        historic_table = DIV(
            DIV(DIV(htable, _class="web2py_htmltable"), _class="web2py_table"),
            _class="web2py_grid",
        )
    else:
        historic_table = ""
    grid_and_buttons = DIV(
        DIV(archive_button),
        DIV(historic_table),
        DIV(grid),
        # DIV("show_archive ", show_archive, BR(), " show_all ", show_all),
    )
    return grid_and_buttons
