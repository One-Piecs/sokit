#include <QComboBox>
#include <QSettings>
#include <QFileInfo>
#include <QDir>
#include <QLockFile>
#include <QFile>

#include "setting.h"

// sokit can run several times at the same time: on macOS a second launch is a
// separate process, on Windows and Linux they simply start another copy. Every
// running instance keeps its own directory, so settings, the notepad and the
// log files do not overwrite each other.
static QLockFile* g_lock = 0;         // held until the instance exits
static QString g_wanted;              // instance name asked for on the command line

int Setting::s_instance = 1;

QString Setting::basePath()
{
	QString path(QDir::currentPath());
    if (!QFileInfo(path).isWritable() ||
        path == QDir::homePath ())
	{
		QDir dir(QDir::home());
		dir.mkdir("." SET_APP_NAME);
		if (dir.cd("." SET_APP_NAME))
			path = dir.absolutePath();
	}

	return path;
}

QString Setting::selectPath()
{
	QString base(basePath());

	// "--instance name" always uses <base>-<name>
	if (!g_wanted.isEmpty())
	{
		QString path(base + "-" + g_wanted);
		seed(path, base);

		g_lock = new QLockFile(path + QDir::separator() + SET_APP_NAME ".lock");
		g_lock->tryLock(200);
		s_instance = 0;

		return path;
	}

	// otherwise take the first directory no other instance is using
	for (int i = 1; i < 32; ++i)
	{
		QString path(i == 1 ? base : base + "-" + QString::number(i));
		seed(path, base);

		QLockFile* lock = new QLockFile(path + QDir::separator() + SET_APP_NAME ".lock");
		if (lock->tryLock(200))
		{
			g_lock = lock;
			s_instance = i;
			return path;
		}

		delete lock;
	}

	return base;
}

// a brand new instance directory starts with a copy of the settings of the
// first instance, so a second window has the same known addresses and ports
void Setting::seed(const QString& path, const QString& base)
{
	if (path == base || QDir(path).exists())
		return;

	if (!QDir().mkpath(path))
		return;

	QString from(base + QDir::separator() + SET_APP_NAME ".ini");
	if (QFile::exists(from))
		QFile::copy(from, path + QDir::separator() + SET_APP_NAME ".ini");
}

Setting::Setting()
{
	QSettings::setPath(QSettings::IniFormat, QSettings::UserScope, selectPath());
}

QSettings& Setting::storage()
{
	static Setting dummy; // to ensure call QSettings::setPath before create the g_settings
	static QSettings g_settings(QSettings::IniFormat, QSettings::UserScope, SET_APP_NAME);
	return g_settings;
}

QString Setting::path()
{
	return QFileInfo(storage().fileName()).dir().absolutePath();
}

QString Setting::instanceLabel()
{
	storage();

	if (!g_wanted.isEmpty())
		return g_wanted;

	return (s_instance > 1) ? QString::number(s_instance) : QString();
}

void Setting::useInstance(const QString& name)
{
	g_wanted = name;
}

void Setting::flush()
{
	storage().sync();
}

void Setting::set(const QString& section, const QString& key, const QString& val)
{
	storage().setValue(section+key, val);
}

QString Setting::get(const QString& section, const QString& key, const QString& def)
{
	return storage().value(section+key, def).toString();
}

void Setting::save(const QString& section, const QString& prefix, const QComboBox& cmb, bool all)
{
	QSettings& store = storage();

	store.beginGroup(section);

	QString tkey = prefix + SET_PFX_CMBTXT;

	QString tval = cmb.currentText().trimmed();
	if (!tval.isEmpty())
		store.setValue(tkey, tval);

	if (all)
	{
		QStringList keys, vals;

		keys = store.childKeys();
		qint32 n = keys.size();
		if (n > 0)
		{
			keys.sort();

			while (n--)
			{
				QString k = keys[n];
				if ((k!=tkey) && k.startsWith(prefix))
				{
					QString v = store.value(k).toString().trimmed();
					if (!v.isEmpty() && (-1 == cmb.findText(v)))
						vals.prepend(v);

					store.remove(k);
				}
			}
		}

		n = cmb.count();
		if (n > SET_MAX_CMBITM)
			n = SET_MAX_CMBITM;

		qint32 i = 0;
		for (i=0; i<n; ++i)
			store.setValue(prefix+QString::number(i), cmb.itemText(i));

		n = (vals.count() > SET_MAX_CMBITM) ? SET_MAX_CMBITM : vals.count();
		for (qint32 j=0; i<n; ++i,++j)
			store.setValue(prefix+QString::number(i), vals[j]);
	}

	store.endGroup();
}

void Setting::lord(const QString& section, const QString& prefix, QComboBox& cmb, bool all)
{
	cmb.clear();

	QSettings& store = storage();

	QStringList keys, vals;

	store.beginGroup(section);

	keys = store.childKeys();
	qint32 n = keys.size();
	if (n > 0)
	{
		QString tval;
		QString tkey = prefix + SET_PFX_CMBTXT;

		keys.sort();

		while (n--)
		{
			QString k = keys[n];
			if (k.startsWith(prefix))
			{
				QString v = store.value(k).toString().trimmed();
				if (k == tkey)
					tval = v;
				else if (all && !v.isEmpty())
					vals.append(v);
			}
		}

		vals.removeDuplicates();

		n = vals.count();
		if (n > 0)
		{
			if (n > SET_MAX_CMBITM)
				n = SET_MAX_CMBITM;

			while (n--)
				cmb.addItem(vals[n]);
		}

		if (!tval.isEmpty())
			cmb.setEditText(tval);
	}

	store.endGroup();
}

