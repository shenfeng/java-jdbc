package {{ns}};

import java.sql.*;


public class {{bean.name}} {% if bean.extends %} extends {{bean.extends}} {% end %} {
{% if bean.static %}
    {% for f in bean.fields_rs %} public static final String {{f.field.upper()}} = "{{f.name.lower()}}";
    {% end %}
{% end %}

    {% for t, name in bean.fields %} public final {{t}} {{name}};
    {% end %}

    public {{bean.name}}(ResultSet rs) throws SQLException{
        {%if bean.extends %}super(rs); {% end %}
        {% for f in bean.fields_rs %}this.{{f.var}} = rs.{{f.method}}("{{f.field}}");
        {% end %}
    }

    public String toString() {
    {% if bean.extends %}
        StringBuffer sb = new StringBuffer(super.toString());
    {% else %}
        StringBuffer sb = new StringBuffer();
    {% end %}
        {% for t, name in bean.fields %}
        sb.append("{{name}}=").append({{name}}).append("\n"); {% end %}
        return sb.toString();
    }
}
