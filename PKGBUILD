# Maintainer: Maisam Musthafa <maisam.musthafa@gmail.com>

pkgname=narnia
pkgver=1.0.0
pkgrel=1
pkgdesc="A curses-based console client for aria2"
arch=('any')
url='http://bitbucket.org/maisammusthafa/narnia'
license=('MIT')

package() {
    #cd "${srcdir}/${pkgname}-${pkgver}"
    cd ..
    python setup.py -q install --root="${pkgdir}" --optimize=1
    rm -rf build src
}
