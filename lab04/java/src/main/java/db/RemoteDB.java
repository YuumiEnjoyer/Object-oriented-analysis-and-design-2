package db;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;
import models.User;

public class RemoteDB extends DB {

    private Connection connection;

    public RemoteDB() {
        super();
        String dbUser = System.getenv("DB_USER");
        String dbPassword = System.getenv("DB_PASSWORD");
        try {
            this.connection = DriverManager.getConnection(
                this.dbPath,
                dbUser,
                dbPassword
            );
            createTables();
        } catch (Exception e) {
            throw new RuntimeException(
                "Failed to initialize PostgreSQL database",
                e
            );
        }
    }

    private void createTables() throws SQLException {
        String sql = """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY NOT NULL,
                username TEXT NOT NULL UNIQUE
            );
            """;

        try (PreparedStatement stmt = connection.prepareStatement(sql)) {
            stmt.execute();
        }
    }

    @Override
    public List<User> getAllUsers() {
        List<User> users = new ArrayList<>();
        String sql = "SELECT * FROM users;";

        try (
            PreparedStatement stmt = connection.prepareStatement(sql);
            ResultSet rs = stmt.executeQuery()
        ) {
            while (rs.next()) {
                User user = new User(rs.getInt("id"), rs.getString("username"));
                users.add(user);
            }
        } catch (SQLException e) {
            throw new RuntimeException("Failed to retrieve users", e);
        }

        return users;
    }

    @Override
    public User registerUser(User user) {
        String sql = "INSERT INTO users (username) VALUES (?) RETURNING id;";

        try (PreparedStatement stmt = connection.prepareStatement(sql)) {
            stmt.setString(1, user.getUsername());

            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    user.setId(rs.getInt("id"));
                }
            }
        } catch (SQLException e) {
            try {
                connection.rollback();
            } catch (SQLException rollbackEx) {
                // ignore
            }
            throw new RuntimeException("Failed to register user", e);
        }

        return user;
    }
}
