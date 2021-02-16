/*
based on helm/internal/sympath
licensed under Apache License, Version 2.0

https://github.com/helm/helm/blob/64c8df187af892c2a9f872f91e892a717df2e7ff/internal/sympath/walk.go
*/

package sympath

import (
	"fmt"
	"os"
	"path/filepath"
	"sort"
)

// Walk walks the file tree rooted at root, calling walkFn for each file or directory
// in the tree, including root. All errors that arise visiting files and directories
// are filtered by walkFn. The files are walked in lexical order, which makes the
// output deterministic but means that for very large directories Walk can be
// inefficient. Walk follows symbolic links.
func Walk(root string, walkFn filepath.WalkFunc) error {
	info, err := os.Lstat(root)
	if err != nil {
		err = walkFn(root, nil, err)
	} else {
		err = symwalk(root, info, walkFn)
	}
	if err == filepath.SkipDir {
		return nil
	}
	return err
}

// readDirNames reads the directory named by dirname and returns
// a sorted list of directory entries.
func readDirNames(dirname string) ([]string, error) {
	f, err := os.Open(dirname)
	if err != nil {
		return nil, err
	}
	names, err := f.Readdirnames(-1)
	_ = f.Close()
	if err != nil {
		return nil, err
	}
	sort.Strings(names)
	return names, nil
}

// symwalk recursively descends path, calling walkFn.
func symwalk(path string, info os.FileInfo, walkFn filepath.WalkFunc) error {
	// Recursively walk symlinked directories.
	if IsSymlink(info) {
		resolved, err := filepath.EvalSymlinks(path)
		if err != nil {
			baseErr := fmt.Errorf("error evaluating symlink %s: %w", path, err)
			if processedErr := walkFn(path, info, baseErr); processedErr != nil && processedErr != filepath.SkipDir {
				return processedErr
			} else {
				return nil
			}
		}
		// log.Printf("found symbolic link in path: %s resolves to %s", path, resolved)
		var resolvedInfo, resolveErr = os.Lstat(resolved)
		if resolveErr != nil {
			if processedErr := walkFn(path, info, resolveErr); processedErr != nil && processedErr != filepath.SkipDir {
				return processedErr
			} else {
				return nil
			}
		}
		if err := symwalk(path, resolvedInfo, walkFn); err != nil && err != filepath.SkipDir {
			return err
		}
		return nil
	}

	if err := walkFn(path, info, nil); err != nil {
		return err
	}

	if !info.IsDir() {
		return nil
	}

	names, err := readDirNames(path)
	if err != nil {
		return walkFn(path, info, err)
	}

	for _, name := range names {
		filename := filepath.Join(path, name)
		fileInfo, err := os.Lstat(filename)
		if err != nil {
			if err := walkFn(filename, fileInfo, err); err != nil && err != filepath.SkipDir {
				return err
			}
		} else {
			err = symwalk(filename, fileInfo, walkFn)
			if err != nil {
				if (!fileInfo.IsDir() && !IsSymlink(fileInfo)) || err != filepath.SkipDir {
					return err
				}
			}
		}
	}
	return nil
}

// IsSymlink is used to determine if the fileinfo is a symbolic link.
func IsSymlink(fi os.FileInfo) bool {
	return fi.Mode()&os.ModeSymlink != 0
}
