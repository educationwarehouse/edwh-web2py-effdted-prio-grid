# Changelog

<!--next-version-placeholder-->

## v0.6.0 (2025-03-04)

### Feature

* Support `gid` in addition to 'id' in grid form urls ([`384b759`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/384b7591bda860eae40c72e4bc1638d0dd5f318b))

## v0.5.3 (2025-02-20)

### Fix

* Show newest on top on 'show all' archive page ([`7f52f92`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/7f52f927ca16e59fc61de5246839bb0e90cac833))

## v0.5.2 (2025-02-10)
* Only call .decode() if bytes are produced ([`ad53d36`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/ad53d3630cd8ccc745aa1df32faa7a21d6696024), ([`e4143fc`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/e4143fcab5bd7d635bd0f5cfe09d860cc251aebf))
* Don't encode table headers, otherwise they show up as `b'id'` ([`04b6231`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/04b6231a10e9e1cb1e52f16ac3620ab9b0c7b401))

## v0.5.1 (2024-10-28)

### Fix

* Use table[field] instead of just field ([`6d8d247`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/6d8d24703cc95e0978ef4be3194195336935a695))

## v0.5.0 (2024-10-28)

### Feature

* Add 'show' as the inverse of 'hide' ([`8c727d8`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/8c727d8688a8ef2bd3509013f6d8647fd78f2e9c))

## v0.4.3 (2024-10-28)

### Fix

* Pop_fields should be optional ([`8cdb087`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/8cdb087dd4198d7e289369799babcb70cb10fee1))

## v0.4.2 (2024-10-16)

### Fix

* Explicit db.commit's after insert ([`4fb41b1`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/4fb41b145cfcecc4b272c4d197bf295b54a5df7f))

## v0.4.1 (2024-10-15)

### Fix

* `keyfieldname` is not always passed in the form on new! ([`95cfd27`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/95cfd27cb1844b6adefaf169ad85ac9a5af8e4bc))

## v0.4.0 (2024-10-15)

### Feature

* **grid:** Allow specifying `pop_fields` to remove certain values when copying a row (e.g. sync_gid) ([`bf87024`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/bf870246cbb78a6bdd3009bf9402135515dedae8))

## v0.3.1 (2024-08-26)

### Fix

* Import BUTTON from yatl ([`bfd4671`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/bfd46713f9611ca54e6d4ac5ee64505a6c765cf6))

## v0.3.0 (2024-08-26)

### Feature

* Add 'restore' option to archive ([`7ed3e7b`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/7ed3e7b3a10868bda97f2bca603e00cf711c5284))

## v0.2.4 (2024-08-26)

### Fix

* Effstatus was set to None after update ([`0273ac2`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/0273ac26fb19dbcc111df9a28758d9d051279112))

## v0.2.3 (2024-08-26)

### Fix

* Confirm with user before deleting something ([`f75c03c`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/f75c03c22f996822cba0039c660e24165a4a9fda))

## v0.2.2 (2024-08-26)

### Fix

* Don't hardcode on 'organisations' table ([`e2f468d`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/e2f468dd4ee92114b1033ce948da68f19b5c5657))
* Don't crash when 'deletable' argument is passed, just hide the delete button in that case ([`ab22727`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/ab22727e166ec1058140c3a7a03801745e0bd117))

## v0.2.1 (2024-08-23)

### Fix

* **archive:** Set([...]) is anders dan {[...]} ([`d0f9396`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/d0f93965c040e11e59d13a3c518d087f886e2eaf))

## v0.2.0 (2024-07-15)

### Feature

* By default, use custom searchable which deals with uuid fields in the db ([`38bbbba`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/38bbbbac8be7b68c103c974a695744e9afe41236))

## v0.1.2 (2024-03-12)

### Fix

* If the form has errors, don't save it. + added typing hints ([`197371a`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/197371a7115a27099b376ba0aafd26a26a11fe5c))

## v0.1.1 (2023-11-08)

### Fix

* Dependency toegevoegd (web2py-gluon) ([`2f83eae`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/2f83eae22e4d4b59ff78305f0a5f8d3af0f9f7cd))
* Version_variable name was incorrect ([`2e2770c`](https://github.com/educationwarehouse/edwh-web2py-effdted-prio-grid/commit/2e2770c4a302a173998e5337ae7b70887c742838))

## v0.1.0 (2023-11-06)
### Fix
* Semantic_release support for automatic changelog building. ([`6c418d4`](https://github.com/remcoboerma/edwh-web2py-effdted-prio-grid/commit/6c418d4ef4bbdc8eea60f2182e3869339d7f6fef))

### Documentation
* Updated repository links ([`b9ef24d`](https://github.com/remcoboerma/edwh-web2py-effdted-prio-grid/commit/b9ef24dcb50eee4232b3a325735ca2b5929a37d7))
