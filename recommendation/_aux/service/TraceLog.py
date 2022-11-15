from recommendation.dataAccess.dataAccess import DataAccess


class TraceLog(object):

    def fetch(self, externalSessionId) -> None:
        dataAccess = DataAccess()
        return dataAccess.getTraceLog(externalSessionId)

    def fetchAll(self, externalSessionId) -> None:
        dataAccess = DataAccess()

        return style + "<h2>Log of " + externalSessionId + ":</h2><br>" + dataAccess.getTraceLogAll(externalSessionId)

    def add(self, externalSessionId, log) -> None:
        dataAccess = DataAccess()
        return dataAccess.addTraceLog(externalSessionId, log)

    def fetchRecord(self, externalSessionId, timestamp):
        dataAccess = DataAccess()
        log = dataAccess.fetchRecord(externalSessionId, timestamp)
        return style + "<h2>Log of " + externalSessionId + ", entry " + timestamp + ":</h2><br><pre style='width:100%;border:1px solid grey;padding:100px'><xmp>" + log.log if log != None else "" + "</xmp></pre>"


style = """<style>
       body {
          background: -webkit-gradient(linear, left top, left bottom, from(#fff), to(grey)) fixed;
        }
                  a {
            background-color: #AAAAAA;
            color: #101010;
          }

          a:hover {
            background-color:  #EEEEEE;
          }

          a:active {
            background-color: #999999;
          }

          a:visited {
            background-color: #888888;
          }</style>
                  """
