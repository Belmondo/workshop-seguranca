"""
Testes funcionais — devem PASSAR com o codigo original e continuar
passando depois das correcoes. Garantem que, ao corrigir uma falha,
o comportamento legitimo da loja nao foi quebrado.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as appmod  # noqa: E402


@pytest.fixture(autouse=True)
def banco():
    os.makedirs(appmod.COMPROVANTES, exist_ok=True)
    appmod.init_db()
    appmod.SESSOES.clear()
    yield


@pytest.fixture
def client():
    return appmod.app.test_client()


def test_login_correto(client):
    r = client.post("/login", json={"email": "ana@exemplo.com", "senha": "ana123"})
    assert r.status_code == 200
    assert "token" in r.get_json()


def test_login_senha_errada(client):
    r = client.post("/login", json={"email": "ana@exemplo.com", "senha": "errada"})
    assert r.status_code == 401


def test_listar_pedidos_do_cliente(client):
    r = client.get("/pedidos?cliente=1&busca=Cafe")
    dados = r.get_json()
    assert len(dados) == 1
    assert dados[0]["descricao"] == "Cafe especial 1kg"


def test_comprovante_legitimo(client):
    r = client.get("/comprovante?arquivo=comp_1.txt")
    assert r.status_code == 200
    assert b"COMPROVANTE" in r.data


def test_pode_ver_pedido_do_dono():
    appmod.init_db()
    ana = {"id": 1}
    assert appmod.pode_ver_pedido(ana, 10) is True


def test_nao_pode_ver_pedido_de_outro():
    appmod.init_db()
    ana = {"id": 1}
    assert appmod.pode_ver_pedido(ana, 20) is False
