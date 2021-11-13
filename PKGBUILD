# Maintainer: Maisam Musthafa <maisam.musthafa@gmail.com>

pkgname=narnia
pkgver=1.1.0
pkgrel=1
pkgdesc="A curses-based console client for aria2"
arch=('any')
url='http://github.com/maisammusthafa/narnia'
license=('MIT')
depends=('python3')
optdepends=(
    'aria2: to run the aria2 RPC server locally'
    )
package() {
    cd ..
    python setup.py -q install --root="${pkgdir}" --optimize=1
    rm -rf build src
}
