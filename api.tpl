package {{ns}};

import javax.sql.DataSource;
import java.sql.*;
import java.util.*;


public class {{class_name}} {
    {% for func in funcs %}
     public static {{func.resp}} {{func.name}} (Connection con {% for idx, (t, name) in enumerate(func.args) %}, {{t}} {{name}} {% end %})
        throws SQLException {
            String sql = "{{func.sql}}";
            {% if func.generate_id %}
            PreparedStatement ps = con.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            {% else %}
            PreparedStatement ps = con.prepareStatement(sql);
            {% end %}
            {% for idx, arg in func.sql_args %}
            ps.setObject({{idx}}, {{arg}}); {% end %}

            {% if func.update_insert %}
            ps.executeUpdate();
            {% else %}
            ResultSet rs = ps.executeQuery();
            {% end %}
            {% if func.resp_is_list %}
            {{func.resp}} results = new ArrayList<>();
            while (rs.next()) {
                {% if "String" == func.resp_bean %}
                    results.add(rs.getString(1));
                {% else %}
                    results.add(new {{func.resp_bean}}(rs));
                {% end %}
            }
            return results;
            {% elif func.generate_id %}
            ResultSet rs = ps.getGeneratedKeys();
            if (rs.next()) {
                return rs.getInt(1);
            }
            return 0;
            {% elif func.is_primitive%}

            if (rs.next()) {
                return rs.{{func.is_primitive[0]}}(1);
            } else {
                return {{func.is_primitive[1]}};
            }

            {% elif func.has_resp %}
            if (rs.next()) {
                return new {{func.resp_bean}}(rs);
            } else {
                return null;
            }
            {% end %}
     }

      public static {{func.resp}} {{func.name}} (DataSource ds {% for idx, (t, name) in enumerate(func.args) %}, {{t}} {{name}} {% end %})
         throws SQLException {
         try(Connection con = ds.getConnection()) {
             {% if func.has_resp %} return {% end %} {{func.name}} (con {% for idx, (t, name) in enumerate(func.args) %},{{name}} {% end %});
         }
      }

        public {{func.resp}} {{func.name}} ({% for idx, (t, name) in enumerate(func.args) %} {{t}} {{name}} {% if idx < len(func.args) - 1 %}, {% end %} {% end %})
           throws SQLException {
           try(Connection con = ds.getConnection()) {
               {% if func.has_resp %} return {% end %} {{func.name}} (con {% for idx, (t, name) in enumerate(func.args) %},{{name}} {% end %});
           }
        }

    {% end %}

    private static String join(List<Integer> ids) {
        StringBuilder sb = new StringBuilder(ids.size() * 7);
        for (Integer id : ids) {
            sb.append(id).append(",");
        }
        sb.setLength(sb.length() - 1);
        return sb.toString();
    }

    public {{class_name}}(DataSource ds) {
        this.ds = ds;
    }

    private final DataSource ds;
}
