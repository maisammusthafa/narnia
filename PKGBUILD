# Maintainer: Maisam Musthafa <maisam.musthafa@gmail.com>

pkgname=narnia2
pkgver=2.0.0
pkgrel=1
pkgdesc="A curses-based console client for aria2"
arch=('any')
url='http://bitbucket.org/maisammusthafa/narnia'
license=('MIT')
depends=('python3')
optdepends=(
    'aria2: to run the aria2 RPC server locally'
    )
package() {
    #cd "${srcdir}/${pkgname}-${pkgver}"
    cd ..
    python setup.py -q install --root="${pkgdir}" --optimize=1
    rm -rf build src
}
