#!/usr/bin/python
import os
import pymysql
import requests
from typing import Optional, Dict, Any

# Database configuration

DB_CONFIG = {
    
}


def get_db_connection() -> Optional[pymysql.Connection]:

    try:
        connection = pymysql.connect(**DB_CONFIG)
        print("Successfully connected to the database")
        return connection
    except pymysql.Error as e:
        print(f"Error connecting to the database: {e}")
        return None


def execute_query(connection: pymysql.Connection, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            connection.commit()
            return None
    except pymysql.Error as e:
        print(f"Error executing query: {e}")
        connection.rollback()
        return None


def execute_sql_file(connection: pymysql.Connection, file_path: str) -> bool:
    try:
        with open(file_path, 'r') as file:
            sql_statements = file.read()

        # Split and execute multiple statements
        for statement in sql_statements.split(';'):
            if statement.strip():
                execute_query(connection, statement)
        return True
    except (IOError, pymysql.Error) as e:
        print(f"Error executing SQL file: {e}")
        return False


def get_codezone_by_template_id(connection: pymysql.Connection, id: str) -> Optional[str]:
    
    try:
        query = "SELECT code_zone_id FROM template WHERE id = %s"
        result = execute_query(connection, query, (id,))
        return result[0]['code_zone_id'] if result else None
    except (pymysql.Error, KeyError, IndexError) as e:
        print(f"Error getting codezoneid for template id {id}: {e}")
        return None



def update_codezone_by_template_id(connection: pymysql.Connection, new_codezoneid: str, id: str) -> bool:
    try:
        query = "UPDATE template SET code_zone_id = %s WHERE id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (new_codezoneid, id))
            connection.commit()
            return cursor.rowcount > 0
    except pymysql.Error as e:
        print(f"Error updating template for templateid {id}: {e}")
        connection.rollback()
        return False


def make_post_request(
    url: str,
    payload: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30
) -> Optional[Dict[str, Any]]:
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=timeout
        )
        response.raise_for_status()
        json_data = response.json()

        # Check response status
        status = json_data.get('status')
        if status != 'success':
            return None

        # Extract data and id safely
        data = json_data.get('data', {})
        resource_id = data.get('id')
        if not resource_id:
            return None

        return {
            'success': True,
            'data': data,
            'id': resource_id
        }
    except requests.exceptions.JSONDecodeError as e:
        return {
            'success': False,
            'error': f'Invalid JSON response: {str(e)}'
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'Request failed: {str(e)}'
        }


def main():
    # 1.调用接口创建新的 codezone 得到 new_codezoneId
    new_codezoneid = '111'
    api_url = "https://develop.clackypaas.com/api/v1/sdk/codeZones/github"
    post_data = {
        "environmentVerId": "403710023458488320",
        "owner": "xiaoyougithub",
        "username": "xiaoyougithub",
        "repo": "simple_html",
        "token": "",
        "unitTestFrameworkId": "",
        "privateKey": "xxxx",
        "ref": "",
        "purpose": "2"
    }
    headers = {
        'tenantCode': 'demo',
        'userId': 'hmj',
    }

    response = make_post_request(
        url=api_url,
        payload=post_data,
        headers=headers,
        timeout=60
    )
    if response and response.get('success'):
        print("POST request successful")
        print("Resource ID:", response.get('id'))
        print("Data:", response.get('data'))
        new_codezoneid = response.get('id')
    else:
        print("POST request failed or invalid response")
        return
    

    

    # 2.建立数据库连接
    connection = get_db_connection()
    if connection is None:
        print("Failed to connect to database")
        return

    # 3. 获取指定 templateid 的 codezoneid , 然后更新
    id=2
    try:
        # Get and display the current email
        current_codezoneid = get_codezone_by_template_id(connection, id)
        if current_codezoneid:
            print(f"Current codezoneid for template {id}: {current_codezoneid}")
        else:
            print(f"No codezoneid found for id {id}")
            return
        

        if update_codezone_by_template_id(connection, new_codezoneid, id):
            print(f"Successfully updated template for {id}")

            # 验证新老codezoneid是否不一致
            updated_codezoneid = get_codezone_by_template_id(connection, id)
            if updated_codezoneid == new_codezoneid:
                print(f"Verified new codezoneid: {updated_codezoneid}")
            else:
                print("Email verification failed")
        else:
            print(f"Failed to update codezoneid for {id}")
            return

    except pymysql.Error as e:
        print(f"Database error occurred: {e}")


    finally:
        # Always close the connection
        connection.close()
        print("\nDatabase connection closed")


if __name__ == "__main__":
    main()