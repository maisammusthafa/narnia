pkgname = narnia-1.0.0-1-any.pkg.tar.xz
install:
	makepkg -f
	sudo pacman -U $(pkgname)
	rm -rf pkg $(pkgname)
