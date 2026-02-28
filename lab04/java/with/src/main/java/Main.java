import db.DB;
import java.awt.*;
import java.util.List;
import javax.swing.*;
import models.User;

public class Main {

    private static JFrame frame;
    private static JTextField usernameField;
    private static JPanel usersPanel;

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> createAndShowGUI());
    }

    private static void createAndShowGUI() {
        frame = new JFrame("DBManager");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setMinimumSize(new Dimension(350, 300));
        frame.setLayout(new BorderLayout());

        // Input panel
        JPanel inputPanel = new JPanel();
        inputPanel.setLayout(new BoxLayout(inputPanel, BoxLayout.Y_AXIS));
        inputPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        JLabel enterLabel = new JLabel("Enter username:");
        enterLabel.setAlignmentX(Component.LEFT_ALIGNMENT);
        inputPanel.add(enterLabel);

        JPanel inputRowPanel = new JPanel();
        inputRowPanel.setLayout(new BoxLayout(inputRowPanel, BoxLayout.X_AXIS));
        inputRowPanel.setAlignmentX(Component.LEFT_ALIGNMENT);

        usernameField = new JTextField();
        usernameField.setMaximumSize(
            new Dimension(200, usernameField.getPreferredSize().height)
        );

        JButton addButton = new JButton("reg user");
        addButton.addActionListener(e -> registerUser());

        inputRowPanel.add(usernameField);
        inputRowPanel.add(Box.createRigidArea(new Dimension(5, 0)));
        inputRowPanel.add(addButton);

        inputPanel.add(Box.createRigidArea(new Dimension(0, 5)));
        inputPanel.add(inputRowPanel);

        frame.add(inputPanel, BorderLayout.NORTH);

        // Users panel with padding
        usersPanel = new JPanel();
        usersPanel.setLayout(new BoxLayout(usersPanel, BoxLayout.Y_AXIS));
        usersPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        JScrollPane scrollPane = new JScrollPane(usersPanel);
        scrollPane.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
        frame.add(scrollPane, BorderLayout.CENTER);

        // Load existing users
        loadExistingUsers();

        frame.setVisible(true);
    }

    private static void registerUser() {
        String username = usernameField.getText().trim();
        if (!username.isEmpty()) {
            User user = new User(username);
            user = DB.getInstance().registerUser(user);
            showUser(user);
        }
        usernameField.setText("");
    }

    private static void showUser(User user) {
        JPanel userPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        userPanel.setBorder(BorderFactory.createRaisedBevelBorder());
        userPanel.setMaximumSize(new Dimension(Integer.MAX_VALUE, 30));

        JLabel userLabel = new JLabel(
            "ID: " + user.getId() + " | Username: " + user.getUsername()
        );
        userPanel.add(userLabel);

        usersPanel.add(userPanel);
        usersPanel.revalidate();
        usersPanel.repaint();
        frame.pack();
    }

    private static void loadExistingUsers() {
        List<User> users = DB.getInstance().getAllUsers();
        for (User user : users) {
            showUser(user);
        }
    }
}
