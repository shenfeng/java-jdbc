package me.shenfeng;

import java.sql.*;


public class Item  {


     public final int id;
     public final String name;
    

    public Item(ResultSet rs) throws SQLException{
        
        this.id = rs.getInt("id");
        this.name = rs.getString("name");
        
    }

    public String toString() {
    
        StringBuffer sb = new StringBuffer();
    
        
        sb.append("id=").append(id).append("\n"); 
        sb.append("name=").append(name).append("\n"); 
        return sb.toString();
    }
}
