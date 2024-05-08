
from qgis.PyQt.QtWidgets import QInputDialog, QMessageBox
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm, QgsProcessingException, 
                       QgsProcessingParameterFeatureSource, QgsProcessingParameterField,
                       QgsProcessingParameterNumber, QgsMessageLog)
from scipy.stats import chisquare, norm
import numpy as np

class TesteAleatoriedadeProcessingAlgorithm(QgsProcessingAlgorithm):

    # ...
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            'camada_a_ser_analisada', 'Layer for randomness test (polygon): Systematized Data', 
            types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterField(
            'campo_esperado', 'Expected Values Field (expected_vals)', '', 'camada_a_ser_analisada'))
        self.addParameter(QgsProcessingParameterField(
            'campo_observado', 'Observed Values Field (observed_vals)', '', 'camada_a_ser_analisada'))
        self.addParameter(QgsProcessingParameterNumber(
            'alfa', 'Alpha value(significance level)', QgsProcessingParameterNumber.Double,
            defaultValue=0.05))

    @staticmethod
    def calcular_valores_criticos(alfa_corrigido):
        # ...
        # Calcular os valores críticos da distribuição normal padrão
        limite_superior = norm.ppf(1 - alfa_corrigido / 2)
        limite_inferior = norm.ppf(alfa_corrigido / 2)
        return limite_superior, limite_inferior


    @staticmethod
    def normalizar_valores(valores):
        # ...
        soma = sum(valores)
        if soma == 0:
            return valores  # Evita divisão por zero
        return [valor / soma for valor in valores]


    def processAlgorithm(self, parameters, context, feedback):
        camada = self.parameterAsVectorLayer(parameters, 'camada_a_ser_analisada', context)
        campo_esperado = self.parameterAsString(parameters, 'campo_esperado', context)
        campo_observado = self.parameterAsString(parameters, 'campo_observado', context)
        alfa = self.parameterAsDouble(parameters, 'alfa', context)


        if not camada:
            raise QgsProcessingException("Camada inválida.")

        # O restante do seu código processAlgorithm vai aqui.
        # Lembre-se de usar 'feedback' para registrar mensagens.

        # Inicializar listas para valores esperados e observados
        valores_esperados = []
        valores_observados = []

        # Acessar os dados da camada e extrair os valores esperados e observados
        for feature in camada.getFeatures():
            valor_esperado = feature[campo_esperado]
            valor_observado = feature[campo_observado]
            if isinstance(valor_esperado, (int, float)) and isinstance(valor_observado, (int, float)):
                valores_esperados.append(float(valor_esperado))
                valores_observados.append(float(valor_observado))

        # Normalizar os valores esperados e observados
        valores_esperados = TesteAleatoriedadeProcessingAlgorithm.normalizar_valores(valores_esperados)
        valores_observados = TesteAleatoriedadeProcessingAlgorithm.normalizar_valores(valores_observados)

        # Executar o teste qui-quadrado de aderência
        chi2, p_valor = chisquare(valores_observados, f_exp=valores_esperados)

        # Calcular os resíduos padronizados ajustados
        res_padronizados = (np.array(valores_observados) - np.array(valores_esperados)) / np.sqrt(valores_esperados)

        # Aplicar a correção de Bonferroni ao valor de alfa
        p_valor_corrigido = p_valor * len(valores_esperados)  # Número de testes multiplicado pelo p-valor original
        alfa_corrigido = alfa / len(valores_esperados)

        # Calcular os valores críticos com base no novo valor de alfa corrigido
        limite_superior, limite_inferior = TesteAleatoriedadeProcessingAlgorithm.calcular_valores_criticos(alfa_corrigido)

        mensagem = "Estatística qui-quadrado: {}\n".format(chi2)
        mensagem += "Valor-p: {}\n".format(p_valor)
        mensagem += "Valor-p corrigido (Bonferroni): {}\n".format(p_valor_corrigido)
        mensagem += "Resíduos Padronizados:\n{}\n".format(res_padronizados)
        mensagem += "Valores críticos para alfa corrigido ({}):\n".format(alfa_corrigido)
        mensagem += "Limite Superior: {}\n".format(limite_superior)
        mensagem += "Limite Inferior: {}\n".format(limite_inferior)
        
        # Interpretar o resultado com a correção de Bonferroni
        if p_valor_corrigido < alfa_corrigido:
            mensagem += "Rejeitar a hipótese nula: A distribuição do fenômeno analisado não possui carácter aleatório (com correção de Bonferroni)."
        else:
            mensagem += "Falha em rejeitar a hipótese nula: A distribuição do fenômeno analisado possui carácter aleatório (com correção de Bonferroni)."

        # Use feedback.pushInfo para registrar a mensagem
        feedback.pushInfo("Resultado do Teste Qui-Quadrado:\n" + mensagem)


        return {}
                
    def name(self):
        return 'Spatial Randomness Test: Point Pattern'

    def displayName(self):
        return 'Spatial Randomness Part2: Chi-square Test'

    def group(self):
        return 'Overlay spatial analysis - Point Pattern'

    def groupId(self):
        return 'Overlay spatial analysis - Point Pattern'

    def createInstance(self):
        return TesteAleatoriedadeProcessingAlgorithm()

    def shortHelpString(self):

        return (
            "<font size='5' face='Arial'><b>This part of plugin execute Chi-square Test in data prepared \
            \n  \
            \n                         PARAMETERS                           \
            \n \
            \n <b>Layer to be analyzed - output of Spatial Randomness Test: Point Pattern - overlay\
            \n \
            \n \
            \n >>> Expected Values Field (expected_vals): in output of Spatial Randomness Test: Point Pattern\
            \n \
            \n \
            \n >>> Observed Values Field (observed_vals): in output of Spatial Randomness Test: Point Pattern\
            \n \
            \n \
            \n \
            \n >>> Alpha value(significance level): usual values 0.10, 0.05 and 0.01\
            \n- \
            \n- \
            \n- Link to ...http..."
            )

            
    def helpUrl(self):
        """
        Returns the URL of the help online
        """
        return 'https://github.com/....'





