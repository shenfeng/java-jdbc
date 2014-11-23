package me.shenfeng;

import javax.sql.DataSource;
import java.sql.*;
import java.util.*;


public class ExampleApi {
    
     public static Item getItemById (Connection con , int id )
        throws SQLException {
            String sql = "select * form item where id = ?";
            
            PreparedStatement ps = con.prepareStatement(sql);
            
            
            ps.setObject(1, id); 

            
            ResultSet rs = ps.executeQuery();
            
            
            if (rs.next()) {
                return new Item(rs);
            } else {
                return null;
            }
            
     }

      public static Item getItemById (DataSource ds , int id )
         throws SQLException {
         try(Connection con = ds.getConnection()) {
              return  getItemById (con ,id );
         }
      }

        public Item getItemById ( int id  )
           throws SQLException {
           try(Connection con = ds.getConnection()) {
                return  getItemById (con ,id );
           }
        }

    
     public static List<Item> getItems (Connection con , int limit , int offset )
        throws SQLException {
            String sql = "select * from item limit ?, ?";
            
            PreparedStatement ps = con.prepareStatement(sql);
            
            
            ps.setObject(1, limit); 
            ps.setObject(2, offset); 

            
            ResultSet rs = ps.executeQuery();
            
            
            List<Item> results = new ArrayList<>();
            while (rs.next()) {
                
                    results.add(new Item(rs));
                
            }
            return results;
            
     }

      public static List<Item> getItems (DataSource ds , int limit , int offset )
         throws SQLException {
         try(Connection con = ds.getConnection()) {
              return  getItems (con ,limit ,offset );
         }
      }

        public List<Item> getItems ( int limit ,   int offset  )
           throws SQLException {
           try(Connection con = ds.getConnection()) {
                return  getItems (con ,limit ,offset );
           }
        }

    
     public static List<Item> getItems (Connection con , List<Integer> ids )
        throws SQLException {
            String sql = "select * from item where id in (" + join(ids) + ") order by FIELD(id, " + join(ids) + ")";
            
            PreparedStatement ps = con.prepareStatement(sql);
            
            

            
            ResultSet rs = ps.executeQuery();
            
            
            List<Item> results = new ArrayList<>();
            while (rs.next()) {
                
                    results.add(new Item(rs));
                
            }
            return results;
            
     }

      public static List<Item> getItems (DataSource ds , List<Integer> ids )
         throws SQLException {
         try(Connection con = ds.getConnection()) {
              return  getItems (con ,ids );
         }
      }

        public List<Item> getItems ( List<Integer> ids  )
           throws SQLException {
           try(Connection con = ds.getConnection()) {
                return  getItems (con ,ids );
           }
        }

    
     public static int saveItem (Connection con , String name )
        throws SQLException {
            String sql = "insert into item (name) value (?)";
            
            PreparedStatement ps = con.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            
            
            ps.setObject(1, name); 

            
            ps.executeUpdate();
            
            
            ResultSet rs = ps.getGeneratedKeys();
            if (rs.next()) {
                return rs.getInt(1);
            }
            return 0;
            
     }

      public static int saveItem (DataSource ds , String name )
         throws SQLException {
         try(Connection con = ds.getConnection()) {
              return  saveItem (con ,name );
         }
      }

        public int saveItem ( String name  )
           throws SQLException {
           try(Connection con = ds.getConnection()) {
                return  saveItem (con ,name );
           }
        }

    
     public static void updateItem (Connection con , int id , String newName )
        throws SQLException {
            String sql = "update item set name = ? where id = ?";
            
            PreparedStatement ps = con.prepareStatement(sql);
            
            
            ps.setObject(1, newName); 
            ps.setObject(2, id); 

            
            ps.executeUpdate();
            
            
     }

      public static void updateItem (DataSource ds , int id , String newName )
         throws SQLException {
         try(Connection con = ds.getConnection()) {
              updateItem (con ,id ,newName );
         }
      }

        public void updateItem ( int id ,   String newName  )
           throws SQLException {
           try(Connection con = ds.getConnection()) {
                updateItem (con ,id ,newName );
           }
        }

    
     public static void deleteItemById (Connection con , int id )
        throws SQLException {
            String sql = "delete from item where id = ?";
            
            PreparedStatement ps = con.prepareStatement(sql);
            
            
            ps.setObject(1, id); 

            
            ResultSet rs = ps.executeQuery();
            
            
     }

      public static void deleteItemById (DataSource ds , int id )
         throws SQLException {
         try(Connection con = ds.getConnection()) {
              deleteItemById (con ,id );
         }
      }

        public void deleteItemById ( int id  )
           throws SQLException {
           try(Connection con = ds.getConnection()) {
                deleteItemById (con ,id );
           }
        }

    

    private static String join(List<Integer> ids) {
        StringBuilder sb = new StringBuilder(ids.size() * 7);
        for (Integer id : ids) {
            sb.append(id).append(",");
        }
        sb.setLength(sb.length() - 1);
        return sb.toString();
    }

    public ExampleApi(DataSource ds) {
        this.ds = ds;
    }

    private final DataSource ds;
}
