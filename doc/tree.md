krbss@MSI MINGW64 /d/EPITECH/bunshinAI (main)
$ find . -print | sed -e 's;[^/]\*/;|**_;g;s;_**|; |;g'
.
|**_.env
|_**.env.example
|***.git
| |***COMMIT_EDITMSG
| |***config
| |***description
| |***HEAD
| |***hooks
| | |***applypatch-msg.sample
| | |***commit-msg.sample
| | |***fsmonitor-watchman.sample
| | |***post-update.sample
| | |***pre-applypatch.sample
| | |***pre-commit.sample
| | |***pre-merge-commit.sample
| | |***pre-push.sample
| | |***pre-rebase.sample
| | |***pre-receive.sample
| | |***prepare-commit-msg.sample
| | |***push-to-checkout.sample
| | |***sendemail-validate.sample
| | |***update.sample
| |***index
| |***info
| | |***exclude
| |***logs
| | |***HEAD
| | |***refs
| | | |***heads
| | | | |***main
| | | |***remotes
| | | | |***origin
| | | | | |***HEAD
| | | | | |***main
| |***objects
| | |***0d
| | | |***5dd443afb95d8f601032a32a184227314315db
| | |***1b
| | | |***980ec831ac142cf75cf1d7d42a90d3a0b439ad
| | |***1d
| | | |***2e7962773f6bd04b562eeb396c4c6f4dba9b3f
| | |***23
| | | |***2232337cc85197e3d9810497e8f941576f44a4
| | |***39
| | | |***273ad786e129da65af97a7e7466adb7f1ea4fc
| | |***3a
| | | |***85a897e4a8784a533f24cf9c85695b538ade72
| | |***3e
| | | |***41e0d7f4f288231ee7628ebad8d66556f17c80
| | |***45
| | | |***fa6ed7b83415cc5e09f9aa8c3b65b905d9274a
| | |***4a
| | | |***06c5749d246e5dcb99d68eb476255afb3f10d9
| | |***4e
| | | |***62ee9ccd8de7a8d18417c2124a6126ee1cebdf
| | |***54
| | | |***b3121639f65547198eb5237ec94244a9e86c3b
| | |***5a
| | | |***a7633fe2e5025753fc3a5058cc225de5b0004a
| | |***7c
| | | |***3ece3bb51ef7e55d07131007bb48f6f75f5789
| | | |***5175f4dcfd31f62bea0528a9f7ce3d816a2cdd
| | |***81
| | | |***3a36fbc9b70a31f479cd688e48bee51650f332
| | |***89
| | | |***258b16a3b2ba12f176c57aaab99945b7d6f754
| | |***8b
| | | |***102699a1be860a8fc4033e1e0cf09c69d384a6
| | |***91
| | | |***2b24fc64beb2f9433ce98ee157b4a6ce554157
| | |***97
| | | |***bc5d8abf88087f5fed24a0f2cef6a4c0dcdc76
| | |***98
| | | |***425a4a62f31a42d486e8aea0f5036f447eabe5
| | |***9d
| | | |***1dcfdaf1a6857c5f83dc27019c7600e1ffaff8
| | |***9e
| | | |***90f1276d4c4740304de9a3afa115afe4e86812
| | |***c5
| | | |***967f4f401af941811d7d08e89fbc1e90d46619
| | |***d5
| | | |***64d0bc3dd917926892c55e3706cc116d5b165e
| | |***da
| | | |***1a45911cba1ecd7b1fb19ae24e426ea233bc4d
| | |***e1
| | | |***0124a7825353740857b1fd631512b2a3acd9fb
| | |***e5
| | | |***28806cab9d87c99857f5d9c49e0765806b817c
| | |***e6
| | | |***9de29bb2d1d6434b8b29ae775ad8c2e48c5391
| | |***f7
| | | |***b7fd72f27ee04a77a35b856fce653b25535e37
| | |***fd
| | | |***0df1c06b89f3884bf1a4084095209e17ce3ce4
| | |***info
| | |***pack
| | | |***pack-55fbbf89e37cc7c95380d8197b6cfe4ff19546d4.idx
| | | |***pack-55fbbf89e37cc7c95380d8197b6cfe4ff19546d4.pack
| | | |***pack-55fbbf89e37cc7c95380d8197b6cfe4ff19546d4.rev
| |***packed-refs
| |***refs
| | |***heads
| | | |***main
| | |***remotes
| | | |***origin
| | | | |***HEAD
| | | | |***main
| | |***tags
|***.github
| |***workflows
|***.gitignore
|***agents_factory
| |**\_**init**.py
|\_**cloud
| |**\_providers
| | |\_\_\_**init**.py
| |\_\_\_**init**.py
|\_**core
| |***brain.py
| |***orchestrator.py
| |**\_resource_monitor.py
| |\_\_\_**init**.py
| |\_\_\_**pycache**
| | |\_**brain.cpython-314.pyc
| | |***orchestrator.cpython-314.pyc
| | |***resource_monitor.cpython-314.pyc
| | |**\_**init**.cpython-314.pyc
|\_**dlmodelAI.sh
|***docker-compose.yml
|***legacy
| |***bunshin_documentation_nettoyee.md
| |***README1.0.md
| |***readme1.4.md
| |***readme_bunshin v2.3.md
|***llamastart.sh
|***log.sh
|***log.txt
|***logs
| |***.gitkeep
|***main.py
|**_memory
| |_**.gitkeep
| |**\_kuzu_db
| |\_\_\_**init**.py
|\_**page3000.sh
|***README_bunshin_v2_5.md
|***relaunch.sh
|***requirements-host.txt
|***roadmap.md
|**\_safety
| |\_\_\_**init**.py
|\_**setup.sh
|**\_tests
| |\_\_\_**init**.py
|\_**ui
| |***api_rest.py
| |***app.py
| |***Dockerfile.api
| |***Dockerfile.streamlit
| |**\_**init**.py
|\_**workspace
| |**_input
| | |_**.gitkeep
| |**_output
| | |_**.gitkeep
