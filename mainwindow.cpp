#include "mainwindow.h"
#include <QApplication>
#include <QDebug>
#include <QDesktopWidget>
#include <QFile>
#include <QTimer>

QString DEMO_CPU = "CPU:%1% MEM:%2%";
QString DEMO_NET = "↓ %1 ↑ %2";
QString DEMO_LAUNCHER = "\
[Desktop Entry]\
Encoding=UTF-8\
Name=Minimalist\
Comment=极简系统监视器\
Exec={}\
Icon={}\
Categories=Application;\
Version={}\
Type=Application\
Terminal=false\
";

// '''人性化显示流量单位'''
QString humanize(float netspeed)
{
    static const char unit[] = {'B', 'K', 'M', 'G', 'T'};
    int n = 0;
    while (netspeed >= 1000) {
        netspeed /= 1024;
        n++;
    }

    n = n >= 5 ? 4 : n;
    return QString::number(netspeed, 10, 2) + unit[n];
}

// ''' 获取cpu、内存占用数据 '''
QString get_cpu_and_mem_date()
{
    const char *PROC_STAT = "/proc/stat";
    const char *PROC_MEM = "/proc/meminfo";

    // CPU
    QFile f(PROC_STAT);
    if (!f.open(QIODevice::ReadOnly))
        return "";
    auto split = QString(f.readLine()).split(' ', Qt::SkipEmptyParts);
    f.close();
    split.removeAt(0);
    auto sum = 0, idle = split[3].toInt();
    for (auto e : split) {
        sum += e.toInt();
    }
    float cpu = 1 - idle * 1.0 / sum;

    // Memory
    f.setFileName(PROC_MEM);
    if (!f.open(QIODevice::ReadOnly))
        return "";
    auto memTotal = QString(f.readLine()).split(' ', Qt::SkipEmptyParts)[1].toInt();
    f.readLine();
    auto memAvailable = QString(f.readLine()).split(' ', Qt::SkipEmptyParts)[1].toInt();
    f.close();
    float mem = 1 - memAvailable * 1.0 / memTotal;

    return DEMO_CPU.arg(cpu * 100, 0, 'g', 3).arg(mem * 100, 0, 'g', 3);
}

// ''' 获取网络数据 '''
QString get_net_date()
{
    static int lastRecv = 0, lastSend = 0;
    QFile f("/proc/net/dev");
    if (!f.open(QIODevice::ReadOnly))
        return "";
    f.readLine();
    f.readLine();
    int recv = 0, send = 0;
    QString buf;
    while ((buf = f.readLine()).length() > 0) {
        auto split = buf.split(' ', Qt::SkipEmptyParts);
        if (split.length() < 9)
            continue;
        recv += split[1].toInt();
        send += split[9].toInt();
    }
    f.close();

    float refRecv = recv - lastRecv, refSend = send - lastSend;
    lastRecv = recv;
    lastSend = send;

    return DEMO_NET.arg(humanize(refRecv)).arg(humanize(refSend));
}

MainWindow::MainWindow(QWidget *parent)
    : QLabel(parent)
{
    auto desktop = QApplication::desktop();
    auto width = desktop->geometry().width();

    move(width / 2 - 100, 0);

    setWindowFlags(Qt::FramelessWindowHint | Qt::WindowStaysOnTopHint | Qt::Tool);
    setWindowModality(Qt::ApplicationModal);

    setFixedWidth(200);
    setFixedHeight(28);

    setAlignment(Qt::AlignCenter);
    setStyleSheet("");
    setText("");

    auto tmr = new QTimer(this);
    tmr->setInterval(1000);
    connect(tmr, &QTimer::timeout, this, &MainWindow::refreshUI);
    tmr->start();
}

MainWindow::~MainWindow()
{
}

void MainWindow::mousePressEvent(QMouseEvent *event)
{
    // 左键移动
    if (event->button() != Qt::LeftButton)
        return;
    auto &pos = event->screenPos();
    leftClick = true;
    offsetX = pos.x() - x();
    offsetY = pos.y() - y();
}

void MainWindow::mouseReleaseEvent(QMouseEvent *event)
{
    if (event->button() == Qt::LeftButton) {
        leftClick = false;
        return;
    }

    // 右键切换cpu、内存、流量显示
    if (event->button() == Qt::RightButton)
        showNet = !showNet;
}

void MainWindow::mouseDoubleClickEvent(QMouseEvent *event)
{
    // 左键换肤、右键退出
    if (event->button() == Qt::RightButton)
        QApplication::exit();
}

void MainWindow::mouseMoveEvent(QMouseEvent *event)
{
    // 左键移动
    if (!leftClick)
        return;
    auto &pos = event->screenPos();
    move(pos.x() - offsetX, pos.y() - offsetY);
}

void MainWindow::refreshUI()
{
    if (showNet)
        setText(get_net_date());
    else
        setText(get_cpu_and_mem_date());
}
