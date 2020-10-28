pkgname = narnia-1.1.0-1-any.pkg.tar.zst
install:
	makepkg -f
	sudo pacman -U $(pkgname)
	rm -rf pkg $(pkgname)
