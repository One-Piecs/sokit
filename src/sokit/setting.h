#ifndef __SETTING_H__
#define __SETTING_H__

#define SET_APP_NAME   "sokit"

#define SET_MAX_CMBITM  10
#define SET_PFX_CMBITM  "item"
#define SET_PFX_CMBTXT  'x'

#define SET_SEC_CFG  "config"
#define SET_SEC_DIR  "dir"
#define SET_KEY_LOG  "/log"

class QComboBox;
class QSettings;
class Setting
{
public:
	static void set(const QString& section, const QString& key, const QString& val);
	static QString get(const QString& section, const QString& key, const QString& def);

	static QString path();
	static QString instanceLabel();
	static void useInstance(const QString& name);

	static void save(const QString& section, const QString& prefix, const QComboBox& cmb, bool all=true);
	static void lord(const QString& section, const QString& prefix, QComboBox& cmb, bool all=true);

	static void flush();
	
private:
	Setting();
	static QString basePath();
	static QString selectPath();
	static void seed(const QString& path, const QString& base);
	static QSettings& storage();

	static int s_instance;
};

#endif // __SETTING_H__

