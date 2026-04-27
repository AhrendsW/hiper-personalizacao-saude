# 01 — Problema, Proposta de Valor e KPIs

## Contexto

A Unimed Nacional atende **4,6 milhões de beneficiários** (sendo 2M diretos e 2,6M por intercâmbio), opera em **92% do território nacional** e está inserida em um sistema com **mais de 2.600 hospitais** e **5.297 municípios**. Em escala dessa magnitude, o atendimento "médio" — o mesmo cuidado para todos — gera dois problemas simultâneos:

1. **Para o beneficiário:** cuidado genérico não previne. Pessoas com perfis muito diferentes (jovem ativo, hipertenso, idoso com mobilidade reduzida) recebem a mesma jornada, e a doença é tratada quando já é cara — clínica e financeiramente.
2. **Para a operadora:** sinistralidade alta, custo de hospitalizações evitáveis, baixa adesão a programas preventivos e atrito no engajamento.

## Pergunta central do case

> **Como criar uma jornada de cuidado hiper personalizada?**

## Proposta de valor

Uma plataforma de cuidado que:

- **Ouve continuamente** o beneficiário através de wearables, app, claims e prontuário
- **Decide** o risco e a melhor ação usando ML clássico auditável
- **Comunica** com tom, canal e momento certos usando GenAI
- **Mede** o impacto clínico e financeiro em tempo quase real
- **Adapta** as trilhas para cada perfil (jovem, crônico, idoso) e evolui com o feedback

O resultado é um modelo em que **cada R$ investido em prevenção retorna em redução de sinistralidade**, e cada beneficiário recebe a intervenção que faz sentido **para ele**, no canal e momento em que ela funciona.

## Quem é atendido

| Perfil | Volume estimado* | Característica | Ganho principal |
|---|---|---|---|
| Jovens saudáveis | ~40% | Vida ativa, baixa frequência médica | Prevenção, hábitos, adesão a check-up |
| Crônicos | ~25% | Hipertensão, diabetes, dislipidemia | Controle contínuo, evitar agudização |
| Idosos | ~15% | Multimorbidade, polifarmácia | Suporte domiciliar, telemedicina, segurança medicamentosa |
| Demais | ~20% | Eventuais e gestantes | Trilhas específicas (não escopo deste protótipo) |

\* *Distribuição ilustrativa. A real virá do warehouse de claims/cadastrais.*

## KPIs de sucesso

A solução é avaliada em **três dimensões** que precisam mover juntas — ganhar em uma e perder em outra invalida a proposta.

### 1. Saúde do beneficiário (clínico)

- Redução de **internações evitáveis** (PQI — Prevention Quality Indicators) em cada coorte
- Redução de **agudizações** em crônicos (ex.: descompensação de hipertensos, crises de diabéticos)
- **Adesão terapêutica** medida por dispensação x prescrição
- **PROMs/PREMs** — instrumentos validados de qualidade percebida e desfecho
- **NPS** específico por trilha de cuidado

### 2. Sinistralidade e operação (financeiro)

- **Custo médico per capita** por coorte de risco
- **Sinistralidade** (custo médico / receita) — meta de redução em 1-3 pontos percentuais em 12 meses
- **Custo de aquisição de evento prevenido** (CAEP) — quanto custou para evitar uma internação
- **Razão de ROI** entre investimento em prevenção e redução de claims

### 3. Engajamento (produto)

- **Taxa de ativação** — beneficiários que conectaram pelo menos um sinal contínuo (app, wearable)
- **Taxa de resposta a recomendações** — % que executou a ação sugerida (consulta, exame, mudança de hábito)
- **D7/D30 retention** no app
- **Tempo médio até primeira ação preventiva**

## Princípios de design

1. **Privacidade não é feature, é restrição** — toda decisão de arquitetura passa pelo filtro LGPD/ANS/CFM antes de virar código.
2. **Auditabilidade clínica** — todo modelo que toca decisão de cuidado precisa ter explicabilidade (SHAP, feature importance).
3. **Humano no loop em decisão clínica** — IA recomenda, profissional de saúde aprova quando o risco passa de um limiar.
4. **Falha segura** — quando o modelo está incerto, escalar para humano, não chutar.
5. **Mensuração antes de escala** — nenhum cuidado novo entra em produção em massa sem ensaio quase-experimental.

## O que está fora do escopo desta proposta

- Solução fim-a-fim de prontuário eletrônico (assumimos integração com EHR existente)
- Faturamento, autorização de procedimentos, glosa
- Marketing institucional e fora-de-uso clínico
