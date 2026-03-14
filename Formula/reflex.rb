class Reflex < Formula
  desc "Claude Code plugin for development workflows, skills, and MCP management"
  homepage "https://github.com/neverprepared/ink-bunny"
  url "https://github.com/neverprepared/ink-bunny/releases/download/reflex-v1.21.0/reflex-1.21.0.tar.gz"
  sha256 "9d6e917e1a212d10c0e05e780cb213c20f2cd436ad2b1bc1f628eedd5dff4d62"
  license "MIT"

  def install
    (share/"reflex").install Dir["plugins/reflex/*"]
  end

  def caveats
    <<~EOS
      To use reflex with Claude Code:

        claude --plugin-dir #{share}/reflex

      Or install from the plugin marketplace:

        /plugin marketplace add mindmorass/reflex
    EOS
  end

  test do
    assert_path_exists share/"reflex/.claude-plugin/plugin.json"
  end
end
