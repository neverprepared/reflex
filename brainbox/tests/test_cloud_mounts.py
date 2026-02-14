"""Tests for cloud CLI credential mounting into containers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from docker.errors import NotFound

from brainbox.config import CloudSettings, Settings
from brainbox.lifecycle import _resolve_cloud_mounts
from brainbox.models import SessionContext


# ---------------------------------------------------------------------------
# CloudSettings defaults
# ---------------------------------------------------------------------------


class TestCloudSettings:
    def test_defaults_all_enabled(self):
        cs = CloudSettings()
        assert cs.mount_aws is True
        assert cs.mount_azure is True
        assert cs.mount_kube is True

    def test_disable_individual_mounts(self):
        cs = CloudSettings(mount_aws=False, mount_azure=False, mount_kube=False)
        assert cs.mount_aws is False
        assert cs.mount_azure is False
        assert cs.mount_kube is False

    def test_settings_includes_cloud(self):
        s = Settings()
        assert hasattr(s, "cloud")
        assert isinstance(s.cloud, CloudSettings)


# ---------------------------------------------------------------------------
# _resolve_cloud_mounts() — host path resolution
# ---------------------------------------------------------------------------


class TestResolveCloudMounts:
    def test_mounts_default_aws_dir(self, tmp_path):
        aws_dir = tmp_path / ".aws"
        aws_dir.mkdir()
        with (
            patch("brainbox.lifecycle.Path.home", return_value=tmp_path),
            patch.dict("os.environ", {}, clear=True),
            patch("brainbox.lifecycle.settings") as mock_settings,
        ):
            mock_settings.cloud = CloudSettings()
            result = _resolve_cloud_mounts()
        assert str(aws_dir) in result
        assert result[str(aws_dir)]["bind"] == "/home/developer/.aws"
        assert result[str(aws_dir)]["mode"] == "ro"

    def test_mounts_aws_from_env_var(self, tmp_path):
        aws_dir = tmp_path / "custom-aws"
        aws_dir.mkdir()
        config_file = aws_dir / "config"
        config_file.touch()
        with (
            patch("brainbox.lifecycle.Path.home", return_value=tmp_path),
            patch.dict("os.environ", {"AWS_CONFIG_FILE": str(config_file)}, clear=True),
            patch("brainbox.lifecycle.settings") as mock_settings,
        ):
            mock_settings.cloud = CloudSettings()
            result = _resolve_cloud_mounts()
        assert str(aws_dir) in result
        assert result[str(aws_dir)]["bind"] == "/home/developer/.aws"

    def test_mounts_aws_from_credentials_env_var(self, tmp_path):
        aws_dir = tmp_path / "other-aws"
        aws_dir.mkdir()
        creds_file = aws_dir / "credentials"
        creds_file.touch()
        with (
            patch("brainbox.lifecycle.Path.home", return_value=tmp_path),
            patch.dict("os.environ", {"AWS_SHARED_CREDENTIALS_FILE": str(creds_file)}, clear=True),
            patch("brainbox.lifecycle.settings") as mock_settings,
        ):
            mock_settings.cloud = CloudSettings()
            result = _resolve_cloud_mounts()
        assert str(aws_dir) in result

    def test_mounts_default_azure_dir(self, tmp_path):
        azure_dir = tmp_path / ".azure"
        azure_dir.mkdir()
        with (
            patch("brainbox.lifecycle.Path.home", return_value=tmp_path),
            patch.dict("os.environ", {}, clear=True),
            patch("brainbox.lifecycle.settings") as mock_settings,
        ):
            mock_settings.cloud = CloudSettings()
            result = _resolve_cloud_mounts()
        assert str(azure_dir) in result
        assert result[str(azure_dir)]["bind"] == "/home/developer/.azure"
        assert result[str(azure_dir)]["mode"] == "ro"

    def test_mounts_azure_from_env_var(self, tmp_path):
        azure_dir = tmp_path / "custom-azure"
        azure_dir.mkdir()
        with (
            patch("brainbox.lifecycle.Path.home", return_value=tmp_path),
            patch.dict("os.environ", {"AZURE_CONFIG_DIR": str(azure_dir)}, clear=True),
            patch("brainbox.lifecycle.settings") as mock_settings,
        ):
            mock_settings.cloud = CloudSettings()
            result = _resolve_cloud_mounts()
        assert str(azure_dir) in result
        assert result[str(azure_dir)]["bind"] == "/home/developer/.azure"

    def test_mounts_default_kube_dir(self, tmp_path):
        kube_dir = tmp_path / ".kube"
        kube_dir.mkdir()
        with (
            patch("brainbox.lifecycle.Path.home", return_value=tmp_path),
            patch.dict("os.environ", {}, clear=True),
            patch("brainbox.lifecycle.settings") as mock_settings,
        ):
            mock_settings.cloud = CloudSettings()
            result = _resolve_cloud_mounts()
        assert str(kube_dir) in result
        assert result[str(kube_dir)]["bind"] == "/home/developer/.kube"
        assert result[str(kube_dir)]["mode"] == "ro"

    def test_mounts_kube_from_env_var(self, tmp_path):
        kube_dir = tmp_path / "custom-kube"
        kube_dir.mkdir()
        kubeconfig = kube_dir / "config"
        kubeconfig.touch()
        with (
            patch("brainbox.lifecycle.Path.home", return_value=tmp_path),
            patch.dict("os.environ", {"KUBECONFIG": str(kubeconfig)}, clear=True),
            patch("brainbox.lifecycle.settings") as mock_settings,
        ):
            mock_settings.cloud = CloudSettings()
            result = _resolve_cloud_mounts()
        assert str(kube_dir) in result
        assert result[str(kube_dir)]["bind"] == "/home/developer/.kube"

    def test_skips_missing_directories(self, tmp_path):
        """No dirs exist → no mounts."""
        with (
            patch("brainbox.lifecycle.Path.home", return_value=tmp_path),
            patch.dict("os.environ", {}, clear=True),
            patch("brainbox.lifecycle.settings") as mock_settings,
        ):
            mock_settings.cloud = CloudSettings()
            result = _resolve_cloud_mounts()
        assert result == {}

    def test_skips_disabled_mounts(self, tmp_path):
        """Dirs exist but settings disable them."""
        (tmp_path / ".aws").mkdir()
        (tmp_path / ".azure").mkdir()
        (tmp_path / ".kube").mkdir()
        with (
            patch("brainbox.lifecycle.Path.home", return_value=tmp_path),
            patch.dict("os.environ", {}, clear=True),
            patch("brainbox.lifecycle.settings") as mock_settings,
        ):
            mock_settings.cloud = CloudSettings(
                mount_aws=False, mount_azure=False, mount_kube=False
            )
            result = _resolve_cloud_mounts()
        assert result == {}

    def test_partial_mounts(self, tmp_path):
        """Only AWS exists → only AWS mounted."""
        (tmp_path / ".aws").mkdir()
        with (
            patch("brainbox.lifecycle.Path.home", return_value=tmp_path),
            patch.dict("os.environ", {}, clear=True),
            patch("brainbox.lifecycle.settings") as mock_settings,
        ):
            mock_settings.cloud = CloudSettings()
            result = _resolve_cloud_mounts()
        assert len(result) == 1
        binds = [v["bind"] for v in result.values()]
        assert "/home/developer/.aws" in binds


# ---------------------------------------------------------------------------
# provision() — cloud mounts in volumes
# ---------------------------------------------------------------------------


class TestProvisionCloudMounts:
    @pytest.mark.asyncio
    async def test_provision_includes_cloud_volumes(self, tmp_path):
        aws_dir = tmp_path / ".aws"
        aws_dir.mkdir()
        azure_dir = tmp_path / ".azure"
        azure_dir.mkdir()

        mock_client = MagicMock()
        mock_image = MagicMock()
        mock_image.attrs = {"RepoDigests": []}
        mock_client.images.get.return_value = mock_image
        mock_client.containers.get.side_effect = NotFound("not found")
        mock_client.containers.create.return_value = MagicMock()

        cloud_mounts = {
            str(aws_dir): {"bind": "/home/developer/.aws", "mode": "ro"},
            str(azure_dir): {"bind": "/home/developer/.azure", "mode": "ro"},
        }

        with (
            patch("brainbox.lifecycle._docker", return_value=mock_client),
            patch("brainbox.lifecycle._find_available_port", return_value=7681),
            patch("brainbox.lifecycle._verify_cosign", new_callable=AsyncMock),
            patch("brainbox.lifecycle._resolve_cloud_mounts", return_value=cloud_mounts),
        ):
            from brainbox.lifecycle import provision

            ctx = await provision(session_name="cloud-test")

        create_call = mock_client.containers.create.call_args
        volumes = create_call[1]["volumes"]
        assert str(aws_dir) in volumes
        assert volumes[str(aws_dir)]["bind"] == "/home/developer/.aws"
        assert volumes[str(aws_dir)]["mode"] == "ro"
        assert str(azure_dir) in volumes
        assert "aws" in ctx.cloud_mounts
        assert "azure" in ctx.cloud_mounts

    @pytest.mark.asyncio
    async def test_provision_no_cloud_when_dirs_missing(self):
        mock_client = MagicMock()
        mock_image = MagicMock()
        mock_image.attrs = {"RepoDigests": []}
        mock_client.images.get.return_value = mock_image
        mock_client.containers.get.side_effect = NotFound("not found")
        mock_client.containers.create.return_value = MagicMock()

        with (
            patch("brainbox.lifecycle._docker", return_value=mock_client),
            patch("brainbox.lifecycle._find_available_port", return_value=7681),
            patch("brainbox.lifecycle._verify_cosign", new_callable=AsyncMock),
            patch("brainbox.lifecycle._resolve_cloud_mounts", return_value={}),
        ):
            from brainbox.lifecycle import provision

            ctx = await provision(session_name="no-cloud-test")

        assert ctx.cloud_mounts == set()


# ---------------------------------------------------------------------------
# start() — cloud env var injection
# ---------------------------------------------------------------------------


class TestStartCloudEnvVars:
    @pytest.fixture()
    def ctx_with_cloud(self):
        return SessionContext(
            session_name="cloud-env-test",
            container_name="developer-cloud-env-test",
            port=7681,
            created_at=0,
            ttl=3600,
            hardened=False,
            cloud_mounts={"aws", "azure", "kube"},
        )

    @pytest.fixture()
    def ctx_without_cloud(self):
        return SessionContext(
            session_name="no-cloud-env-test",
            container_name="developer-no-cloud-env-test",
            port=7682,
            created_at=0,
            ttl=3600,
            hardened=False,
            cloud_mounts=set(),
        )

    @pytest.mark.asyncio
    async def test_writes_cloud_env_file(self, ctx_with_cloud):
        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_container.exec_run.return_value = (0, b"")
        mock_client.containers.get.return_value = mock_container

        sessions = {ctx_with_cloud.session_name: ctx_with_cloud}
        with (
            patch("brainbox.lifecycle._docker", return_value=mock_client),
            patch("brainbox.lifecycle._sessions", sessions),
        ):
            from brainbox.lifecycle import start

            await start(ctx_with_cloud)

        # Find the cloud_env exec_run call
        calls = mock_container.exec_run.call_args_list
        cloud_env_calls = [
            c
            for c in calls
            if any(".cloud_env" in str(arg) for arg in c.args + tuple(c.kwargs.values()))
        ]
        assert len(cloud_env_calls) >= 1
        cmd_str = str(cloud_env_calls[0])
        assert "AWS_CONFIG_FILE" in cmd_str
        assert "AZURE_CONFIG_DIR" in cmd_str
        assert "KUBECONFIG" in cmd_str

    @pytest.mark.asyncio
    async def test_skips_cloud_env_when_no_mounts(self, ctx_without_cloud):
        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_container.exec_run.return_value = (0, b"")
        mock_client.containers.get.return_value = mock_container

        sessions = {ctx_without_cloud.session_name: ctx_without_cloud}
        with (
            patch("brainbox.lifecycle._docker", return_value=mock_client),
            patch("brainbox.lifecycle._sessions", sessions),
        ):
            from brainbox.lifecycle import start

            await start(ctx_without_cloud)

        calls = mock_container.exec_run.call_args_list
        cloud_env_calls = [
            c
            for c in calls
            if any(".cloud_env" in str(arg) for arg in c.args + tuple(c.kwargs.values()))
        ]
        assert len(cloud_env_calls) == 0
