"""Testes da legalidade dos lances: cravada, xeque, roque e en passant."""

from app.domain.board import Tabuleiro
from app.domain.casa import Casa
from app.domain.cor import Cor
from app.domain.moves.validador import ValidadorDeLances
from app.domain.pieces import Peao

validador = ValidadorDeLances()


def _legais(tabuleiro: Tabuleiro) -> set[str]:
    return {str(lance) for lance in validador.gerar_legais(tabuleiro, tabuleiro.vez)}


def test_peca_cravada_nao_pode_se_mover():
    # Bispo branco em e2 cravado pela torre preta em e8 contra o rei em e1.
    tabuleiro = Tabuleiro.de_fen("4r2k/8/8/8/8/8/4B3/4K3 w - - 0 1")
    legais = _legais(tabuleiro)
    assert not any(lance.startswith("e2") for lance in legais)


def test_em_xeque_so_restam_lances_que_defendem():
    # Rei branco em e1 sob xeque da torre preta em e8; só lances do rei que
    # saem da coluna e resolvem o xeque são legais.
    tabuleiro = Tabuleiro.de_fen("4r2k/8/8/8/8/8/8/4K3 w - - 0 1")
    legais = _legais(tabuleiro)
    assert legais == {"e1d1", "e1f1", "e1d2", "e1f2"}


def test_roque_dos_dois_lados_disponivel():
    tabuleiro = Tabuleiro.de_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    legais = _legais(tabuleiro)
    assert "e1g1" in legais  # roque curto
    assert "e1c1" in legais  # roque longo


def test_roque_proibido_ao_passar_por_casa_atacada():
    # Torre preta em f8 ataca f1: o rei branco não pode rocar curto.
    tabuleiro = Tabuleiro.de_fen("4kr2/8/8/8/8/8/8/R3K2R w KQ - 0 1")
    legais = _legais(tabuleiro)
    assert "e1g1" not in legais
    assert "e1c1" in legais  # o roque longo continua válido


def test_execucao_do_roque_move_a_torre():
    tabuleiro = Tabuleiro.de_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    roque_curto = next(l for l in validador.gerar_legais(tabuleiro, Cor.BRANCA) if str(l) == "e1g1")
    tabuleiro.aplicar_lance(roque_curto)
    assert tabuleiro.peca_em(Casa.de_algebrica("g1")) is not None  # rei
    assert tabuleiro.peca_em(Casa.de_algebrica("f1")) is not None  # torre
    assert tabuleiro.esta_vazia(Casa.de_algebrica("h1"))


def test_captura_en_passant_remove_o_peao_certo():
    tabuleiro = Tabuleiro.de_fen("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1")
    lance_ep = next(
        l for l in validador.gerar_legais(tabuleiro, Cor.BRANCA)
        if l.eh_en_passant
    )
    assert str(lance_ep) == "e5d6"
    tabuleiro.aplicar_lance(lance_ep)
    assert isinstance(tabuleiro.peca_em(Casa.de_algebrica("d6")), Peao)
    assert tabuleiro.esta_vazia(Casa.de_algebrica("d5"))  # peão preto capturado


def test_avanco_duplo_registra_alvo_en_passant():
    tabuleiro = Tabuleiro.inicial()
    lance = next(l for l in validador.gerar_legais(tabuleiro, Cor.BRANCA) if str(l) == "e2e4")
    tabuleiro.aplicar_lance(lance)
    assert tabuleiro.alvo_en_passant == Casa.de_algebrica("e3")


def _snapshot(tabuleiro: Tabuleiro) -> dict[str, str]:
    return {casa.algebrica: peca.simbolo_fen for casa, peca in tabuleiro.casas.items()}


def test_simulacao_nao_altera_o_tabuleiro_original():
    # A geração de lances legais simula em cópias; o original deve ficar intacto.
    tabuleiro = Tabuleiro.inicial()
    antes = _snapshot(tabuleiro)
    validador.gerar_legais(tabuleiro, Cor.BRANCA)
    assert _snapshot(tabuleiro) == antes
    assert tabuleiro.vez is Cor.BRANCA
