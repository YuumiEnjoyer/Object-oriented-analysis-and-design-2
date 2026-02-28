package db;

import java.util.List;
import java.util.ServiceLoader;
import java.util.ServiceLoader.Provider;
import java.util.stream.StreamSupport;
import models.User;

public abstract class DB {

    private static DB instance;
    protected String dbPath;

    public DB() {
        this.dbPath = System.getenv().getOrDefault("DB_PATH", "");
        if (this.dbPath.isEmpty()) {
            throw new RuntimeException("DB_PATH environment variable not set");
        }
    }

    public static synchronized DB getInstance() {
        if (instance == null) {
            instance = getPlugin();
        }
        return instance;
    }

    private static DB getPlugin() {
        String pluginName = System.getenv("DB_TYPE");
        if (pluginName == null || pluginName.isEmpty()) {
            throw new RuntimeException("DB_TYPE environment variable not set");
        }

        try {
            pluginName =
                pluginName.substring(0, 1).toUpperCase() +
                pluginName.substring(1);
            return (DB) Class.forName("db." + pluginName + "DB").newInstance();
        } catch (Exception e) {
            throw new RuntimeException(
                "`" + pluginName + "` DB plugin not implemented",
                e
            );
        }
    }

    public abstract List<User> getAllUsers();

    public abstract User registerUser(User user);
}
