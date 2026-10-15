from agentshell.policy.policy import check, Decision


def test_env_denied():
    assert check("cat .env").decision == Decision.DENY
    assert check("cat /home/user/project/.env").decision == Decision.DENY

def test_ssh_denied():
    assert check("ls ~/.ssh").decision == Decision.DENY
    assert check("cat ~/.ssh/id_rsa").decision == Decision.DENY

def test_rm_rf_denied():
    assert check("rm -rf /").decision == Decision.DENY
    assert check("rm -rf ~").decision == Decision.DENY

def test_safe_allowed():
    assert check("ls -la").decision == Decision.ALLOW
    assert check("python run.py").decision == Decision.ALLOW
    assert check("git status").decision == Decision.ALLOW


if __name__ == "__main__":
    # Простой прогон без pytest, если его нет
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"OK: {t.__name__}")
    print(f"\nВсего: {len(tests)} тестов, все прошли")