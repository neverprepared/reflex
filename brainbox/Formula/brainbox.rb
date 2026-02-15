class Brainbox < Formula
  include Language::Python::Virtualenv

  desc "Sandboxed Docker container orchestration for Claude Code"
  homepage "https://github.com/neverprepared/ink-bunny"
  url "https://github.com/neverprepared/ink-bunny/releases/download/brainbox/v0.4.0/brainbox-0.4.0.tar.gz"
  sha256 "8c41f0fc4b5c7e75ee44abb63e3ccdc6e70a4e26c093015e5554810423593674"
  license "MIT"

  depends_on "python@3.12"
  depends_on "docker" => :optional

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "brainbox", shell_output("#{bin}/brainbox --help")
  end
end
