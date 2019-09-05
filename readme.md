Mudança de Reservas por Código - Guia do Usuário
================================================

Este artigo tem o intuito de orientar o uso do programa que realiza a troca de reservas.

*   [Introdução](#MudançadeReservasporCódigo-GuiadoUsuário-Introdução)
*   [Instruções](#MudançadeReservasporCódigo-GuiadoUsuário-Instruções)

Introdução
----------

O programa é constituído de três arquivos. São eles:

*   **modify.py** - função auxiliar que implementa a divisão da reserva atual em N reservas menores
*   **exchange.py** - função auxiliar que implementa a troca de uma reserva por outra de plataforma diferente (Linux, Windows, etc) ou tipo de instância EC2 diferente
*   **process-reservation.py** - função principal que orquestra a operação da funções descritas acima

Além disso, o programa conta com um um arquivo que possui os parâmetros de entrada em sintaxe json. Este arquivo é nomeado **input.json**. 

Instruções
----------

  

1.  Abra o arquivo input.json em qualquer editor de texto e edite conforme necessário para uma execução pro programa. Os parâmetro de entrada são os seguintes:
    *   AWSProfile: o perfil configurado via AWS CLI com as credenciais adequadas para as funções serem executadas com sucesso
    *   Region: a região onde encontram-se as reservas
    *   ReservationId: o ID da reserva que possui desperdício
    *   WastedInstanceCount: a quantidade de instâncias que estão sendo desperdiçadas na reserva
    *   T3NanoExpectedInstanceCount: o número de instâncias t3.nano que espera-se com a primeira troca
    *   MaxHourlyPriceDifference: a máxima diferença de custo por hora, entre a reserva original e as novas
    *   T3NanoSplitInstanceCountList: lista onde cada item é a contagem de instâncias de uma nova reserva gerada pela divisão da reserva t3.nano
    *   TargetPlatformList: lista com as plataformas (Linux, Windows, etc) de cada uma das novas reservas desejadas ao fim da execução do programa
    *   TargetInstanceTypeList: lista com os tipos de instância da novas reservas geradas ao fim da execução do programa
        
        **Exemplo: input.json**
        ```json
        {
			"AccountNumber": "518512136469",
			"Region": "us-east-1",
			"RoleName": "reservation-role",
			"ReservationId": "0009b6cf-9ef0-400c-bb00-619b2311551c",
			"WastedInstanceCount": 43,
			"TradeRIParams": {
				"PlatformList": [
				"Linux/UNIX (Amazon VPC)"
				],
				"InstanceCountList": [
				50
				],
				"InstanceTypeList": [
				"t3.nano"
				],
				"MaxPriceDifference": 0.005,
				"SplitInstanceCountList": [
				21,
				29
				]
			},
			"TargetRIsParams": {
				"PlatformList": [
				"SUSE Linux (Amazon VPC)",
				"Linux/UNIX (Amazon VPC)"
				],
				"InstanceCountList": [
				1,
				2
				],
				"InstanceTypeList": [
				"t2.medium",
				"c5.large"
				],
				"MaxPriceDifference": 0.005
			}
		}
        ```
2.  Salve as alterações no arquivo input.json
3.  Abra um terminal, e digite o seguinte comando:
     ```bash
    python process-reservation.py input.json
    ```
    
4.  Aguarde o programa terminar a execução. Alguns dados serão impressos na tela, indicação o decorrer da operação.
