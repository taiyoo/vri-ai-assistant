# Guide de Migration de Base de Données

> [!Avertissement]
> Ce guide est destiné à la migration de la version 0 à la version 1.

Ce guide décrit les étapes de migration des données lors de la mise à jour de Bedrock Chat, qui comprend le remplacement d'un cluster Aurora. La procédure suivante garantit une transition en douceur tout en minimisant les temps d'arrêt et les pertes de données.

## Vue d'ensemble

Le processus de migration implique de scanner tous les bots et de lancer des tâches ECS d'embedding pour chacun d'entre eux. Cette approche nécessite un recalcul des embeddings, ce qui peut être long et entraîner des coûts supplémentaires en raison de l'exécution des tâches ECS et des frais d'utilisation de Bedrock Cohere. Si vous souhaitez éviter ces coûts et ces contraintes de temps, veuillez consulter les [options de migration alternatives](#alternative-migration-options) présentées plus loin dans ce guide.

## Étapes de migration

- Après [npx cdk deploy](../README.md#deploy-using-cdk) avec le remplacement Aurora, ouvrez le script [migrate_v0_v1.py](./migrate_v0_v1.py) et mettez à jour les variables suivantes avec les valeurs appropriées. Les valeurs peuvent être référencées dans l'onglet `CloudFormation` > `BedrockAIAssistantStack` > `Sorties`.

```py
# Ouvrez la pile CloudFormation dans la console de gestion AWS et copiez les valeurs à partir de l'onglet Sorties.
# Clé : DatabaseConversationTableNameXXXX
TABLE_NAME = "BedrockAIAssistantStack-DatabaseConversationTableXXXXX"
# Clé : EmbeddingClusterNameXXX
CLUSTER_NAME = "BedrockAIAssistantStack-EmbeddingClusterXXXXX"
# Clé : EmbeddingTaskDefinitionNameXXX
TASK_DEFINITION_NAME = "BedrockAIAssistantStackEmbeddingTaskDefinitionXXXXX"
CONTAINER_NAME = "Container"  # Pas besoin de changer
# Clé : PrivateSubnetId0
SUBNET_ID = "subnet-xxxxx"
# Clé : EmbeddingTaskSecurityGroupIdXXX
SECURITY_GROUP_ID = "sg-xxxx"  # BedrockAIAssistantStack-EmbeddingTaskSecurityGroupXXXXX
```

- Exécutez le script `migrate_v0_v1.py` pour lancer le processus de migration. Ce script va analyser tous les bots, lancer des tâches ECS d'intégration et créer les données dans le nouveau cluster Aurora. Notez que :
  - Le script nécessite `boto3`.
  - L'environnement nécessite des autorisations IAM pour accéder à la table DynamoDB et invoquer des tâches ECS.

## Options de Migration Alternative

Si vous préférez ne pas utiliser la méthode précédente en raison des implications de temps et de coût, considérez les approches alternatives suivantes :

### Restauration d'Instantané et Migration DMS

Tout d'abord, notez le mot de passe pour accéder au cluster Aurora actuel. Ensuite, exécutez `npx cdk deploy`, qui déclenchera le remplacement du cluster. Après cela, créez une base de données temporaire en restaurant à partir d'un instantané de la base de données originale.
Utilisez [AWS Database Migration Service (DMS)](https://aws.amazon.com/dms/) pour migrer les données de la base de données temporaire vers le nouveau cluster Aurora.

Remarque : Au 29 mai 2024, DMS ne prend pas nativement en charge l'extension pgvector. Cependant, vous pouvez explorer les options suivantes pour contourner cette limitation :

Utilisez la [migration homogène de DMS](https://docs.aws.amazon.com/dms/latest/userguide/dm-migrating-data.html), qui exploite la réplication logique native. Dans ce cas, les bases de données source et cible doivent être PostgreSQL. DMS peut utiliser la réplication logique native à cette fin.

Tenez compte des exigences et contraintes spécifiques de votre projet lors du choix de l'approche de migration la plus adaptée.