class ShellProfiler < Formula
  desc "Workspace profile manager using direnv for environment-specific configurations"
  homepage "https://github.com/neverprepared/ink-bunny"
  version "0.3.0"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/neverprepared/ink-bunny/releases/download/shell-profiler/v#{version}/shell-profiler-v#{version}-darwin-arm64.tar.gz"
      sha256 "6f71d9bb511f87542da6dc435db513125c3f78c65e388e1e5d871cd6bbc57cdc" # darwin-arm64
    end
    if Hardware::CPU.intel?
      url "https://github.com/neverprepared/ink-bunny/releases/download/shell-profiler/v#{version}/shell-profiler-v#{version}-darwin-amd64.tar.gz"
      sha256 "a795c361c6b1d6f5312b90b9fb3fc6bbd3d873b33f69ecc05c12ce32fd202546" # darwin-amd64
    end
  end

  on_linux do
    if Hardware::CPU.arm?
      url "https://github.com/neverprepared/ink-bunny/releases/download/shell-profiler/v#{version}/shell-profiler-v#{version}-linux-arm64.tar.gz"
      sha256 "8bbc77e6ae3d0ef8980bd47262d7dc745085c09cfd7da6e7e269adaa1f346551" # linux-arm64
    end
    if Hardware::CPU.intel?
      url "https://github.com/neverprepared/ink-bunny/releases/download/shell-profiler/v#{version}/shell-profiler-v#{version}-linux-amd64.tar.gz"
      sha256 "5a70e164a9d93ba8e7e1f0a0c69d6216c5d0b9b195ffa1655be05f8573cfc471" # linux-amd64
    end
  end

  depends_on "direnv"

  def install
    bin.install "shell-profiler"
  end

  test do
    assert_match "Workspace Profile Manager", shell_output("#{bin}/shell-profiler help")
  end
end
