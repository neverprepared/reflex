class Reflex < Formula
  desc "Claude Code plugin for development workflows, skills, and MCP management"
  homepage "https://github.com/neverprepared/ink-bunny"
  url "https://github.com/neverprepared/ink-bunny/releases/download/reflex-v1.13.3/reflex-1.13.3.tar.gz"
  sha256 "ca7f614a7b5bd86be3cda9517ca32d473a17f934524e64256a1a2a918e1b4e14"
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
    assert_predicate share/"reflex/.claude-plugin/plugin.json", :exist?
  end
end
