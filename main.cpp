#include "mainwindow.h"

#include <QApplication>
#include <QSharedMemory>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);

    QSharedMemory share("NetSpeed.04917115240e");
    if (share.attach()) {
        printf("another program is running\n");
        return 1;
    }

    share.create(sizeof(bool));

    MainWindow w;
    w.show();

    return a.exec();
}
