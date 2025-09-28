#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>

#include "OrchestratorClient.hpp"

int main(int argc, char *argv[]) {
  QGuiApplication app(argc, argv);

  QQmlApplicationEngine engine;
  qmlRegisterSingletonInstance("EVSim", 1, 0, "Orchestrator", new evsim::ui::OrchestratorClient(&engine));

  const QUrl url(u"qrc:/qt/qml/EVSim/Main.qml"_qs);
  QObject::connect(&engine, &QQmlApplicationEngine::objectCreated, &app,
                   [url](QObject *obj, const QUrl &objUrl) {
                     if (!obj && url == objUrl)
                       QCoreApplication::exit(-1);
                   },
                   Qt::QueuedConnection);
  engine.load(url);

  return app.exec();
}

