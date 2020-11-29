import configparser,pymysql
from string import Template

# db config
def getConfig(key):
    cf = configparser.ConfigParser()
    cf.read("/Users/boht/tools/EbeanDomainGen/config.ini",encoding='utf-8')
    return cf.get('DB', key)

# assign data to template file and generate domain file
def assignTemplate(data):
    template_file_path = '/Users/boht/tools/EbeanDomainGen/domain.template'
    file = open(template_file_path,'r')
    template_str = file.read()
    template = Template(template_str)
    return template.substitute(data)

# get all table name
def getAllTable():
    sql = "select table_name from information_schema.tables where table_schema='"+getConfig('db')+"'"
    execute = cursor.execute(sql)
    all_table_name = cursor.fetchall()
    return all_table_name

def gen(table_name):
    data = {}
    class_name = "".join(map(lambda x: x.capitalize(), table_name.split("_")))
    sql = """
    SELECT
    COLUMN_NAME 字段名称,
    data_type 数据类型,
    IS_NULLABLE 是否为NULL,
    CHARACTER_MAXIMUM_LENGTH F_DATALENGTH,
    NUMERIC_PRECISION 精度,
    NUMERIC_SCALE 小数位数,
IF
    ( IS_NULLABLE = 'YES', '1', '0' ) F_ALLOWNULL,
    COLUMN_COMMENT F_FIELDNAME,
IF
    ( COLUMN_KEY = 'PRI', '1', '0' ) F_PRIMARYKEY,
    column_default F_DEFAULTS,
    CONCAT( upper( COLUMN_NAME ), '(', COLUMN_COMMENT, ')' ) AS 'F_DESCRIPTION' 
FROM
    INFORMATION_SCHEMA.COLUMNS 
WHERE
    TABLE_NAME = 'user' 
    AND TABLE_SCHEMA = 'shop'
"""
    execute = cursor.execute(sql)
    all_fields = cursor.fetchall()
    field_content = ""
    for field in all_fields:
        if (field[1] == "varchar" or field[1] == "text"):
            field_type = "String"
        elif (field[1] == "date"):
            field_type = "LocalDate"
        elif (field[1] == "int"):
            field_type = "Integer"
        elif (field[1] == "datetime" or field[1] == "timestamp"):
            field_type = "Timestamp"
        elif (field[1] == "float"):
            field_type = "Double"
        elif (field[1] == "numeric"):
            field_type = "java.math.BigDecimal"
        elif (field[1] == "bool"):
            field_type = "Boolean"
        else:
            field_type = field[1]
        # is nullable
        null_able = '' if (field[1] != "YES") else "@NotNull \n"
        # index_type
        index_type = '@id\n' if field[-3] == 1 else ""

        # SIZE
        size = '@Size(max = ' + str(field[3]) + ')\n' if (field[3] is not None) else ''
        # column_name
        column = '@Column(name = "' + field[0] if(field[3] is None) else '@Column(name = "' + field[0] + '",length = ' + str(field[3])
        if (field[1] == "YES"):
            column = column + "',' nullable = false)\n"
        else:
            column = column + ")\n"
        # class field
        class_field = "public " + field_type + " " + field[0] + ";\n"

        field_content = index_type + field_content  + null_able  + size + column + class_field + "\n"
        data['filelds_content'] = field_content
        data['package_name'] = class_name
        data['table_name'] = table_name
        rs = assignTemplate(data)
    print(rs)
    with open("./domain/" +class_name+".java",'a') as file_obj:
        file_obj.write(rs)


if __name__ == '__main__':
    db = pymysql.connect(getConfig('host'),getConfig('username'),getConfig('password'),getConfig('db'))
    cursor = db.cursor()
    all_table_name = getAllTable()

    for table_name in all_table_name:
        gen(table_name[0])

