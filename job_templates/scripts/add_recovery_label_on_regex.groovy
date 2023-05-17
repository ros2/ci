  if(!regex) {
    return """println('WARNING! Incorrect recovery configuration : No regex provided as search key for log')"""
  }
  return """\
    import hudson.model.*
    def node = build.getBuiltOn()
    def oldLabels = node.getLabelString()

    println('# BEGIN SECTION: AGENT RECOVERY PROCESS')
    if (!(build.getLog(1000) =~ ${regex})) {
         println('${error} not detected in the log - Not performing any recovery automatic recovery step')
         return 1;
    } else {
     try {
         println(' PROBLEM: ${error} was detected in the log. Try to automatically resolve it:')
         println("Removing labels and adding 'recovery-process' label to node")
         node.setLabelString('recovery-process')
         } catch (Exception ex) {
         println('ERROR - CANNOT PERFORM RECOVERY ACTIONS FOR NVIDIA ERROR')
         println('Restoring to previous state') node.setLabelString(oldLabels)
         throw ex
     }
    }
    println('# END SECTION: NVIDIA MISMATCH RECOVERY')
  """.stripIndent()
  


