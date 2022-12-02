# Cromshell Package Releases

Cromshell can be installed from a brew tap or through pypi. Having these sources
updated to have the latest releases of Cromshell is important.

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
  resource "pygments" do
    url "https://files.pythonhosted.org/packages/b7/b3/5cba26637fe43500d4568d0ee7b7362de1fb29c0e158d50b4b69e9a40422/Pygments-2.10.0.tar.gz"
    sha256 "f398865f7eb6874156579fdf36bc840a03cab64d1cde9e93d68f46a425ec52c6"
  end
  # below are dependencies of requests
  resource "urllib3" do
    url "https://files.pythonhosted.org/packages/80/be/3ee43b6c5757cabea19e75b8f46eaf05a2f5144107d7db48c7cf3a864f73/urllib3-1.26.7.tar.gz"
    sha256 "4987c65554f7a2dbf30c18fd48778ef124af6fab771a377103da0585e2336ece"
  end
  resource "certifi" do
    url "https://files.pythonhosted.org/packages/6c/ae/d26450834f0acc9e3d1f74508da6df1551ceab6c2ce0766a593362d6d57f/certifi-2021.10.8.tar.gz"
    sha256 "78884e7c1d4b00ce3cea67b44566851c4343c120abd683433ce934a68ea58872"
  end
  resource "charset-normalizer" do
    url "https://files.pythonhosted.org/packages/9f/c5/334c019f92c26e59637bb42bd14a190428874b2b2de75a355da394cf16c1/charset-normalizer-2.0.7.tar.gz"
    sha256 "e019de665e2bcf9c2b64e2e5aa025fa991da8720daa3c1138cadd2fd1856aed0"
  end
  resource "idna" do
    url "https://files.pythonhosted.org/packages/62/08/e3fc7c8161090f742f504f40b1bccbfc544d4a4e09eb774bf40aafce5436/idna-3.3.tar.gz"
    sha256 "9d643ff0a55b762d5cdb124b8eaa99c66322e2157b69160bc32796e824360e6d"
  end
  resource "requests" do
    url "https://files.pythonhosted.org/packages/e7/01/3569e0b535fb2e4a6c384bdbed00c55b9d78b5084e0fb7f4d0bf523d7670/requests-2.26.0.tar.gz"
    sha256 "b8aa58f8cf793ffd8782d3d8cb19e66ef36f7aba4353eec859e74678b01b07a7"
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


## Pypi
Currently, Cromshell is available on testpypi, later it will be made available on 
the main pypi site. 

A git action is available to help easily send a release to pypi. The action needs to be
executed manually with `PyPI_Repo` (by default set to "testpypi" for now) and `version` inputs.

Once a release version is created in the pypi repository, it is not possible rewrite over it
(like in the case of a bug fix) so it's best to allow a release to have in the 'wild' for 
testing before adding the release to pypi.  
