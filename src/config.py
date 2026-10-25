class DevelopmentConfig():
    DEBUG=True
    MYSQL_HOST='localhost'
    MYSQL_USER='angel'
    MYSQL_PASSWORD= 'root'
    MYSQL_DB='api_utl'
    MYSQL_CURSORCLASS='Cursor'

config={
    'development':DevelopmentConfig
}