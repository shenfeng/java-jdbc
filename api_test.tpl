package {{ns}};

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;


public class DBApiTest {

    public void testAbc() {

    }

    public static void main(String[] args) throws SQLException {
        Connection con = DriverManager.getConnection("jdbc:mysql://localhost/jobs", "root", "");
        // Connection con = DriverManager.getConnection("jdbc:mysql://192.168.1.11/kanzhun", "root", "root1234");
        {% for func in funcs %}
//        System.out.println(DBApi.{{func.name}}(con, {% for idx, (t, name) in enumerate(func.args) %}{{name}}{% if idx + 1 < len(func.args) %},{% end %} {% end %}));
    {% end %}
    }
}
