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
            instance = new LocalDB();
            // instance = new RemoteDB();
        }
        return instance;
    }

    public abstract List<User> getAllUsers();

    public abstract User registerUser(User user);
}
