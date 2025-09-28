#pragma once

#include <QObject>
#include <QString>
#include <QVariantMap>

namespace evsim::ui {

class OrchestratorClient : public QObject {
  Q_OBJECT
  Q_PROPERTY(QString lastRunId READ lastRunId NOTIFY lastRunIdChanged)

public:
  explicit OrchestratorClient(QObject *parent = nullptr);

  Q_INVOKABLE QString runScenario(const QVariantMap &scenarioDefinition);
  Q_INVOKABLE QVariantMap fetchRunMetadata(const QString &runId) const;

  QString lastRunId() const { return m_lastRunId; }

signals:
  void lastRunIdChanged();
  void runFailed(const QString &runId, const QString &errorCode, const QString &message);

private:
  QString m_lastRunId;
  QVariantMap m_lastMetadata;
};

} // namespace evsim::ui

