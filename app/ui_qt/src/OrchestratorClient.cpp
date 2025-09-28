#include "OrchestratorClient.hpp"

#include <QUuid>

using namespace evsim::ui;

OrchestratorClient::OrchestratorClient(QObject *parent)
    : QObject(parent) {}

QString OrchestratorClient::runScenario(const QVariantMap &scenarioDefinition) {
  const QString runId = QUuid::createUuid().toString(QUuid::WithoutBraces);
  m_lastRunId = runId;
  m_lastMetadata = scenarioDefinition;
  m_lastMetadata.insert("run_id", runId);
  emit lastRunIdChanged();
  return runId;
}

QVariantMap OrchestratorClient::fetchRunMetadata(const QString &runId) const {
  if (runId == m_lastRunId) {
    return m_lastMetadata;
  }
  QVariantMap placeholder;
  placeholder.insert("run_id", runId);
  placeholder.insert("status", "unknown");
  return placeholder;
}

