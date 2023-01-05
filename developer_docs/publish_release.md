# Cromshell Package Releases

Cromshell can be installed from a brew tap or through pypi. Instructions on how to publish to these repos are detailed below.

## Brew Tap

Regular update of broadinstitute/dsp tap is needed as new releases of Cromshell are made. 
Once a release occurs a new formula for that release should be created in
[broadinstitute/homebrew-dsp](https://github.com/broadinstitute/homebrew-dsp) git repository
in the Formula directory.

The name of the formula file should have the following structure:
`cromshell@[version].rb`. For example:

    cromshell@1.0.3.rb


The following should be updated regularly in a new formula file:
- Git release tar file url
- Git release tar file hash (e.g. `shasum -a 256 /path/to/tar/cromshell-2.0.0.beta.1.tar.gz`)
- List of required python package url and their hash

Here is an example of the content of the Formula file.
```Ruby
class CromshellAT200Alpha1 < Formula
  include Language::Python::Virtualenv

  desc "Python tool to interact with a Cromwell server"
  homepage "https://github.com/broadinstitute/cromshell"
  url "https://github.com/broadinstitute/cromshell/archive/refs/tags/2.0.0.alpha.1.tar.gz"
  sha256 "0ac3604ff362fdf2107f91c886887856098f1731d2d1a9e9cff59278b7b292b9"
  license "BSD-3-Clause"
  depends_on "python@3.9"

  resource "termcolor" do
    url "https://files.pythonhosted.org/packages/8a/48/a76be51647d0eb9f10e2a4511bf3ffb8cc1e6b14e9e4fab46173aa79f981/termcolor-1.1.0.tar.gz"
    sha256 "1d6d69ce66211143803fbc56652b41d73b4a400a2891d7bf7a1cdf4c02de613b"
  end
  resource "click>=8.0.0" do
    url "https://files.pythonhosted.org/packages/f4/09/ad003f1e3428017d1c3da4ccc9547591703ffea548626f47ec74509c5824/click-8.0.3.tar.gz"
    sha256 "410e932b050f5eed773c4cda94de75971c89cdb3155a72a0831139a79e5ecb5b"
  end

  def install
    virtualenv_install_with_resources
  end

  # `test do` will create, run in, and delete a temporary directory.
  test do
    system "#{bin}/cromshell-alpha", "--help"
  end
end
```

Note: 
1. All packages listed in the requirements.txt file should be listed in the formula.
Sometimes packages in the file have their own dependencies, you can identify this
by using a tool like `pipdeptree` to list whether it has dependencies. 
   ```shell
       >pipdeptree -p requests
       requests==2.27.1
       - certifi [required: >=2017.4.17, installed: 2020.12.5]
       - charset-normalizer [required: ~=2.0.0, installed: 2.0.12]
       - idna [required: >=2.5,<4, installed: 2.10]
       - urllib3 [required: >=1.21.1,<1.27, installed: 1.26.2]  
   ```

2. The package url and hash can be obtained from the package pypi site or using a tool like
homebrew-pypi-poet. 

   ```
   poet requests
   ```

   results to: 
   
   ```
     resource "certifi" do
       url "https://files.pythonhosted.org/packages/06/a9/cd1fd8ee13f73a4d4f491ee219deeeae20afefa914dfb4c130cfc9dc397a/certifi-2020.12.5.tar.gz"
       sha256 "1a4995114262bffbc2413b159f2a1a480c969de6e6eb13ee966d470af86af59c"
     end
   
     resource "charset-normalizer" do
       url "https://files.pythonhosted.org/packages/56/31/7bcaf657fafb3c6db8c787a865434290b726653c912085fbd371e9b92e1c/charset-normalizer-2.0.12.tar.gz"
       sha256 "2857e29ff0d34db842cd7ca3230549d1a697f96ee6d3fb071cfa6c7393832597"
     end
   
     resource "idna" do
       url "https://files.pythonhosted.org/packages/ea/b7/e0e3c1c467636186c39925827be42f16fee389dc404ac29e930e9136be70/idna-2.10.tar.gz"
       sha256 "b307872f855b18632ce0c21c5e45be78c0ea7ae4c15c828c20788b26921eb3f6"
     end
   
     resource "requests" do
       url "https://files.pythonhosted.org/packages/60/f3/26ff3767f099b73e0efa138a9998da67890793bfa475d8278f84a30fec77/requests-2.27.1.tar.gz"
       sha256 "68d7c56fd5a8999887728ef304a6d12edc7be74f1cfa47714fc8b414525c9a61"
     end
   
     resource "urllib3" do
       url "https://files.pythonhosted.org/packages/29/e6/d1a1d78c439cad688757b70f26c50a53332167c364edb0134cadd280e234/urllib3-1.26.2.tar.gz"
       sha256 "19188f96923873c92ccb987120ec4acaa12f0461fa9ce5d3d0772bc965a39e08"
     end
   ```
### Test Install

Test installation using formula.
   ```
   brew install --build-from-source cromshell@2.0.0.beta.1.rb
   ```

Test installation using brew tap
   ```
   brew tap broadinstitute/dsp
   brew install cromshell
   ```

## Pypi
Use steps below to release on either PyPi or testPyPi, the latter is primarily used for 
draft releases.

1. Install the following tools

   `python3 -m pip install --upgrade pip twine build`

2. Update the version tag and project name in pyproject.toml. If creating a release in 
`testPyPi` use project name `cromshell-draft-release`, if creating a release in `PyPi`
use project name `cromshell`. 

3. In the root repository directory build cromshell. This will create a folder called `/dist` with tar files of the cromshell build.

   `python3 -m build`
       
4. Publish build using twine. The [PYPI Token](https://pypi.org/help/#apitoken) is obtained from your pypi account, your
   account will need access permission to the cromwell project in pypi (you will have different tokens for testpypi and pypi repos).

   `python3 -m twine upload --username __token__ --password <PYPI_TOKEN> --repository <testpypi/pypi> dist/*`

### Pypi git action [Not Available]
*Because this git yml is only initiated through `workflow dispatch`, the action will not be
functional until the `cromshell2` branch is merged to `main`.*  

A git action has been created to help easily send a release to pypi. The action needs to be
executed manually with `PyPI_Repo` (by default set to "testpypi" for now) and `version` inputs.

Once a release version is created in the pypi repository, it is not possible rewrite over it
(like in the case of a bug fix) so it's best to allow a release to have in the 'wild' for 
testing before adding the release to pypi.  
