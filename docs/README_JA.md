![](https://github.com/mwouts/jupytext/blob/17aea37c612f33a4e27eeee4b81966f1506920fd/docs/images/logo_large.png?raw=true)

<!-- INDEX-START -->

[![CI](https://github.com/mwouts/jupytext/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/mwouts/jupytext/actions)
[![Documentation Status](https://readthedocs.org/projects/jupytext/badge/?version=latest)](https://jupytext.readthedocs.io/en/latest/?badge=latest)
[![codecov.io](https://codecov.io/github/mwouts/jupytext/coverage.svg?branch=main)](https://codecov.io/gh/mwouts/jupytext/branch/main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub language count](https://img.shields.io/github/languages/count/mwouts/jupytext)](./languages.md)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/jupytext.svg)](https://anaconda.org/conda-forge/jupytext)
[![Pypi](https://img.shields.io/pypi/v/jupytext.svg)](https://pypi.python.org/pypi/jupytext)
[![pyversions](https://img.shields.io/pypi/pyversions/jupytext.svg)](https://pypi.python.org/pypi/jupytext)
[![Binder:lab](https://img.shields.io/badge/binder-jupyterlab-0172B2.svg)](https://mybinder.org/v2/gh/mwouts/jupytext/main?urlpath=lab/tree/demo/get_started.ipynb)
[![Binder:notebook](https://img.shields.io/badge/binder-notebook-0172B2.svg)](https://mybinder.org/v2/gh/mwouts/jupytext/main?filepath=demo)
[![launch - renku](https://renkulab.io/renku-badge.svg)](https://renkulab.io/projects/best-practices/jupytext/sessions/new?autostart=1)
[![](https://img.shields.io/badge/YouTube-JupyterCon%202020-red.svg)](https://www.youtube.com/watch?v=SDYdeVfMh48)

# Jupytext

<a href="README_JA.md"><img src="https://img.shields.io/badge/ドキュメント-日本語-white.svg" alt="JA doc"/></a>
<a href="../README.md"><img src="https://img.shields.io/badge/english-document-white.svg" alt="EN doc"></a>

Jupyter Notebookがプレーンテキストドキュメントだったらいいのに、と思ったことはありませんか？お気に入りのIDEで編集できて、バージョン管理時に明確で意味のある差分が得られたら。そんな時は、Jupytextこそまさにあなたが探し求めているツールかもしれません！

## テキストノートブック

`py:percent` [フォーマット](./formats-scripts.md#the-percent-format)でエンコードされたPythonノートブックは、`.py`拡張子を持ち、以下のようになります。

```
# %% [markdown]
# これはマークダウンセルです

# %%
def f(x):
  return 3*x+1
```

ノートブックの入力（とオプションでメタデータ）のみが含まれます。テキストノートブックはバージョン管理に適しています。IDEで編集やリファクタリングも可能です。上記の`.py`ノートブックは通常のPythonファイルです。

コードを主に含むノートブックには`percent`フォーマットをお勧めします。`percent`フォーマットは、Julia、Python、Rなど多くの[言語](./languages.md)で利用可能です。

ノートブックがドキュメント指向の場合は、[Markdownベースのフォーマット](./formats-markdown.md)（`.md`拡張子のテキストノートブック）の方が適切かもしれません。ノートブックの用途に応じて、Jupyter Bookとの相互運用性に優れたMyst Markdownフォーマット、Quarto Markdown、さらにはPandoc Markdownを選ぶのも良いでしょう。

## インストール

JupyterのPython環境にJupytextをインストールします。以下のどちらかを使用します。

    pip install jupytext

または

    conda install jupytext -c conda-forge

その後、Jupyter Labサーバーを再起動し、JupyterでJupytextが有効になっていることを確認します。`.py`と`.md`ファイルにはノートブックのアイコンが表示され、Jupyter Labで右クリックしてノートブックとして開くことができます。

![](https://github.com/mwouts/jupytext/blob/64b4be818508760116f91bf156342cb4cf724d93/docs/images/jupyterlab_right_click.png?raw=true)

## ペアノートブック

`.py`や`.md`拡張子のテキストノートブックはバージョン管理に適しています。IDEで簡単に編集や作成ができます。Jupyter Labで右クリックするとノートブックとして開いて実行できます。ただし、テキストノートブックにはノートブックの入力のみが保存されるため、ノートブックを閉じるとノートブックの出力は失われます。

テキストノートブックの便利な代替手段は、[ペアノートブック](./paired-notebooks.md)です。これは、`.ipynb`と`.py`のように、同じノートブックを異なるフォーマットで含む2つのファイルのセットです。

ペアノートブックの`.py`バージョンを編集し、Jupyterで _reload notebook from disk_ を選択することで、編集内容をJupyterに反映させることができます。`.ipynb`ファイルが存在する場合、出力はそこから再読み込みされます。次にJupyterでノートブックを保存すると、`.ipynb`バージョンが更新または再作成されます。

Jupyter Labでノートブックをペアリングするには、コマンドパレットから`Pair Notebook with percent Script`コマンドを使用します。

![](https://github.com/mwouts/jupytext/blob/64b4be818508760116f91bf156342cb4cf724d93/docs/images/pair_commands.png?raw=true)

特定のディレクトリ内のすべてのノートブックをペアリングするには、以下の内容で[設定ファイル](./config.md)を作成します。

```
# jupytext.toml ノートブックディレクトリのルートに配置
formats = "ipynb,py:percent" 
```

## コマンドライン

Jupytextは[コマンドライン](./using-cli.md)でも利用可能です。以下のことができます。

- `jupytext --set-formats ipynb,py:percent notebook.ipynb`でノートブックをペアリングする
- `jupytext --sync notebook.py`でペアファイルを同期する（入力は最新のペアファイルから読み込まれる）
- `jupytext --to ipynb notebook.py`でノートブックを別のフォーマットに変換する（特定の出力ファイルを指定する場合は`-o`を使用）
- `jupytext --pipe black notebook.ipynb`のようにノートブックをリンターにパイプで渡す

## 使用例

### バージョン管理下のノートブック

手順は以下の通りです。
- Jupyterで`.ipynb`ノートブックを開き、Jupyter Labの _pair_ コマンドまたはグローバルな[設定ファイル](./config.md)を使用して、`.py`ノートブックに[ペアリング](./paired-notebooks.md)します
- ノートブックを保存すると、`.py`ノートブックが作成されます
- この`.py`ノートブックをバージョン管理に追加します

バージョン管理から`.ipynb`ファイルを除外しても構いません（出力もバージョン管理したい場合を除く）。ユーザーが`.py`ノートブックを開いて保存すると、Jupytextがローカルに`.ipynb`ファイルを再作成します。

### Gitでノートブックをコラボレーション

Gitを通じたJupyter Notebookでのコラボレーションが、テキストファイルでのコラボレーションと同じくらい簡単になります。

`.py`ノートブックをバージョン管理下に置いているとします（上記参照）。そうすると、
- コラボレーターが`.py`ノートブックをプルします
- Jupyterでそれを _ノートブックとして_ 開きます（Jupyter Labで右クリック）
- この時点では、ノートブックには出力がありません。ノートブックを実行して保存します。出力が再生成され、ローカルの`.ipynb`ファイルが作成されます
- ノートブックを編集し、更新された`notebook.py`ファイルをプッシュします。差分は、Pythonスクリプトの標準的な差分に他なりません。
- 更新された`notebook.py`スクリプトをプルし、ブラウザを更新します。入力セルは`notebook.py`の新しい内容に基づいて更新されます。出力はローカルの`.ipynb`ファイルから再読み込みされます。最後に、カーネル変数はそのままなので、新しい出力を得るために変更されたセルのみを実行するオプションがあります。

### IDEでのノートブックの編集やリファクタリング

ノートブックを`.py`ファイルと[ペアリング](./paired-notebooks.md)すると、IDEでノートブックの`.py`表現を簡単に編集したりリファクタリングしたりできます。

`.py`ノートブックの編集が終わったら、Jupyterでノートブックを _reload_ するだけで、最新の編集内容がそこに反映されます。

注：ペアリングされた`.py`ファイルを編集するときは、Jupyterで`.ipynb`ノートブックを閉じておくのがシンプルです。そうする義務はありませんが、そうしないのであれば、ポップアップメッセージを注意深く読む準備が必要です。最後のリロード以降にペアリングされた`.py`ファイルもディスク上で編集されている間にJupyterがノートブックを保存しようとすると、競合が検出され、ノートブックのどのバージョン（メモリ内またはディスク上）が適切かを決定するよう求められます。

## その他のリソース

[ドキュメント](https://jupytext.readthedocs.io)でJupytextについてさらに詳しく読むことができます。

Jupytextを初めて使う場合は、[FAQ](./faq.md)または[チュートリアル](./tutorials.md)から始めるのが良いかもしれません。

Jupytextの短い紹介動画もあります。[![](https://img.shields.io/badge/YouTube-JupyterCon%202020-red.svg)](https://www.youtube.com/watch?v=SDYdeVfMh48)