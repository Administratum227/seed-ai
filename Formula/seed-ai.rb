class SeedAi < Formula
  include Language::Python::Virtualenv

  desc "Scalable Ecosystem for Evolving Digital Agents"
  homepage "https://github.com/Administratum227/seed-ai"
  url "https://github.com/Administratum227/seed-ai/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "TODO" # Will be updated on first release
  license "MIT"

  depends_on "python@3.9"
  depends_on "openssl"
  depends_on "sqlite"
  depends_on "git"

  resource "aiohttp" do
    url "https://files.pythonhosted.org/packages/aiohttp.tar.gz"
    sha256 "TODO"
  end

  resource "pyyaml" do
    url "https://files.pythonhosted.org/packages/pyyaml.tar.gz"
    sha256 "TODO"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/rich.tar.gz"
    sha256 "TODO"
  end

  resource "typer" do
    url "https://files.pythonhosted.org/packages/typer.tar.gz"
    sha256 "TODO"
  end

  resource "textual" do
    url "https://files.pythonhosted.org/packages/textual.tar.gz"
    sha256 "TODO"
  end

  def install
    virtualenv_install_with_resources
    
    # Create necessary directories
    (var/"seed").mkpath
    (var/"seed/logs").mkpath
    (var/"seed/data").mkpath
    (var/"seed/cache").mkpath
    
    # Install default configuration
    config = share/"seed/config.yaml"
    config.write(default_config)
  end

  def default_config
    <<~EOS
      # SEED AI Framework Configuration
      version: 1.0.0
      
      runtime:
        max_agents: 10
        task_concurrency: 5
        log_level: INFO
      
      api:
        brave_api_key: ""  # Set via environment variable
        github_token: ""   # Set via environment variable
      
      agents:
        default_capabilities:
          - basic_reasoning
          - task_planning
        max_memory_mb: 1024
        startup_timeout_sec: 30
      
      dashboard:
        port: 8501
        theme: dark
        auto_launch: true
    EOS
  end

  def post_install
    # Ensure user-specific configuration directory exists
    (ENV["HOME"]/"/.seed").mkpath
  end

  test do
    assert_match "SEED AI Framework", shell_output("#{bin}/seed --version")
  end
end