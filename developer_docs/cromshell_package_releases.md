# Cromshell Package Releases

Cromshell can be installed from a brew tap or through pypi. 

## Brew Tap

Regular update of broadinstitute/dsp tap is needed as new releases of Cromshell are made. 
Once a release occurs a new formula for that release should be created in
[broadinstitute/homebrew-dsp](https://github.com/broadinstitute/homebrew-dsp) git repository
in the Formula directory.

The name of the formula file should have the following structure:
`cromshell@[version].rb`. For example:

    cromshell@1.0.3.rb


The following should be updated regularly in a new formula file:
- Git release tag url
- Git release tag hash
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
python hashin. 

   ```
   import hashin
   hashin.get_package_hashes('requests', version='2.27.1')
   ```

   results to: 
   
   ```
   {'package': 'requests', 'version': '2.27.1', 'hashes': [{'hash': '68d7c56fd5a8999887728ef304a6d12edc7be74f1cfa47714fc8b414525c9a61'}, {'hash': 'f22fa1e554c9ddfd16e6e41ac79759e17be9e492b3587efa038054674760e72d'}]}
   ```
### Test Install

   ```
   brew tap broadinstitute/dsp
   brew install cromshell
   ```

## Pypi
Use steps below to release on either PyPi or testPyPi, the latter is primarily used for 
draft releases.

1. Install the following tools

   `python3 -m pip install --upgrade pip twine build`

2. In the root repository directory build cromshell

   `python3 -m build`

3. Update the version tag and project name in pyproject.toml. If creating a release in 
`testPyPi` use project name `cromshell-draft-release`, if creating a release in `PyPi`
use project name `cromshell`. 
       
4. Publish build using twine. The [PYPI Token](https://pypi.org/help/#apitoken) is obtained from your pypi account, your
   account will need access permission to the cromwell project in pypi.

   `python3 -m twine upload --username __token__ --password <test/PYPI_TOKEN> --repository pypi dist/*`

### Pypi git action [Not Available]
*Because this git yml is only initiated through `workflow dispatch`, the action will not be
functional until the `cromshell2` branch is merged to `main`.*  

A git action has been created to help easily send a release to pypi. The action needs to be
executed manually with `PyPI_Repo` (by default set to "testpypi" for now) and `version` inputs.

Once a release version is created in the pypi repository, it is not possible rewrite over it
(like in the case of a bug fix) so it's best to allow a release to have in the 'wild' for 
testing before adding the release to pypi.  
