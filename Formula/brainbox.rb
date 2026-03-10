class Brainbox < Formula
  desc "Docker-based sandboxed Claude Code session manager"
  homepage "https://github.com/neverprepared/ink-bunny"
  url "https://github.com/neverprepared/ink-bunny/releases/download/brainbox/v0.12.9/brainbox-0.12.9.tar.gz"
  version "0.12.9"
  sha256 "b6d842199cbbc1ca9d7df84765c4359626de88417cd7d309f231970dbe8ede78"
  license "MIT"

  depends_on "docker"

  def install
    # Install docker-compose.yml
    (share/"brainbox").install "docker-compose.yml"

    # Create compose-aware wrapper script
    (bin/"brainbox").write <<~EOS
      #!/bin/bash
      # brainbox — Docker Compose wrapper
      set -e

      COMPOSE_FILE="#{share}/brainbox/docker-compose.yml"
      BRAINBOX_VERSION="#{version}"

      # Check if Docker is installed
      if ! command -v docker &> /dev/null; then
          echo "Error: Docker is not installed." >&2
          exit 1
      fi

      # Check if Docker daemon is running
      if ! docker info &> /dev/null 2>&1; then
          echo "Error: Docker is not running. Please start Docker Desktop." >&2
          exit 1
      fi

      case "$1" in
        up|start)
          exec docker compose -f "$COMPOSE_FILE" up -d
          ;;
        down|stop)
          exec docker compose -f "$COMPOSE_FILE" down
          ;;
        logs)
          exec docker compose -f "$COMPOSE_FILE" logs -f
          ;;
        status|ps)
          exec docker compose -f "$COMPOSE_FILE" ps
          ;;
        pull)
          exec docker compose -f "$COMPOSE_FILE" pull
          ;;
        version|--version|-v)
          echo "brainbox $BRAINBOX_VERSION"
          ;;
        *)
          echo "Usage: brainbox {up|start|down|stop|logs|status|pull|version}"
          echo ""
          echo "Commands:"
          echo "  up/start   Start brainbox stack (API + Qdrant)"
          echo "  down/stop  Stop brainbox stack"
          echo "  logs       Follow logs from all services"
          echo "  status     Show running containers"
          echo "  pull       Pull latest images"
          echo "  version    Show brainbox version"
          exit 1
          ;;
      esac
    EOS

    chmod 0755, bin/"brainbox"
  end

  def caveats
    <<~EOS
      brainbox requires Docker to run. Please ensure Docker Desktop is running:
        open -a Docker

      Start the brainbox stack:
        brainbox up

      The API will be available at http://localhost:9999

      Configuration is stored in ~/.config/brainbox
      Qdrant data is stored in ~/.config/brainbox/qdrant (override with QDRANT_DATA_DIR)
    EOS
  end

  test do
    assert_match "brainbox #{version}", shell_output("#{bin}/brainbox version")
  end
end
