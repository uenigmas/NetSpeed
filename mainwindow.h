#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QLabel>
#include <QMouseEvent>

class MainWindow : public QLabel
{
    Q_OBJECT

  public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();
    void mousePressEvent(QMouseEvent *event) override;
    void mouseReleaseEvent(QMouseEvent *event) override;
    void mouseDoubleClickEvent(QMouseEvent *event) override;
    void mouseMoveEvent(QMouseEvent *event) override;

  public slots:
    void refreshUI();

  private:
    QPointF press;
    int offsetX = 50, offsetY = 50;
    bool leftClick = false;
    bool showNet = true;
};
#endif // MAINWINDOW_H
