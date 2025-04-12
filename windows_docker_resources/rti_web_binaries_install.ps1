 write-output ROS_DISTRO $Env:ROS_DISTRO
 write-output CONNEXTDDS_DIR $Env:CONNEXTDDS_DIR
 if ( $Env:ROS_DISTRO -eq "jammy" -or $Env:ROS_DISTRO -eq "humble" ) {
	pixi run 7z x -oC:\connext "C:\TEMP\rticonnextdds-src\openssl-1.1.1k-target-x64Win64VS2017.zip"
	& "C:\TEMP\rticonnextdds-src\rti_connext_dds-6.0.1-pro-host-x64Win64.exe" @("--mode", "unattended", "--unattendedmodeui", "minimalWithDialogs". "--prefix", "C:\connext")
	cmd.exe /c $Env:CONNEXTDDS_DIR\bin\rtipkginstall.bat -u "C:\TEMP\rticonnextdds-src\openssl-1.1.1k-6.0.1.25-host-x64Win64.rtipkg"
	cmd.exe /c $Env:CONNEXTDDS_DIR\bin\rtipkginstall.bat -u "C:\TEMP\rticonnextdds-src\rti_connext_dds-6.0.1-pro-target-x64Win64VS2017.rtipkg"
	cmd.exe /c $Env:CONNEXTDDS_DIR\bin\rtipkginstall.bat -u "C:\TEMP\rticonnextdds-src\rti_security_plugins-6.0.1.25-host-x64Win64.rtipkg"
	cmd.exe /c $Env:CONNEXTDDS_DIR\bin\rtipkginstall.bat -u "C:\TEMP\rticonnextdds-src\rti_security_plugins-6.0.1.25-target-x64Win64VS2017.rtipkg"
} else {
	$params = @("--mode", "unattended", "--unattendedmodeui", "minimalWithDialogs", "--prefix", "C:\connext")
	& "C:\TEMP\rticonnextdds-src\rti_connext_dds-7.3.0-pro-host-x64Win64.exe" $params
	$ssl_host_params = @("-u", "C:\TEMP\rticonnextdds-src\openssl-3.0.12-7.3.0-host-x64Win64.rtipkg")
	$ssl_target_params = @("-u", "C:\TEMP\rticonnextdds-src\openssl-3.0.12-7.3.0-target-x64Win64VS2017.rtipkg")
	$connext_pro_params = @("-u",  "C:\TEMP\rticonnextdds-src\rti_connext_dds-7.3.0-pro-target-x64Win64VS2017.rtipkg")
	$rti_security_host_params = @("-u",  "C:\TEMP\rticonnextdds-src\rti_security_plugins-7.3.0-host-x64Win64.rtipkg")
	$rti_security_target_params = @("-u", "C:\TEMP\rticonnextdds-src\rti_security_plugins-7.3.0-target-x64Win64VS2017.rtipkg")

	cmd.exe /c "$Env:CONNEXTDDS_DIR\bin\rtipkginstall.bat" $ssl_host_params
	cmd.exe /c "$Env:CONNEXTDDS_DIR\bin\rtipkginstall.bat" $ssl_target_params
	cmd.exe /c "$Env:CONNEXTDDS_DIR\bin\rtipkginstall.bat" $connext_pro_params
	cmd.exe /c "$Env:CONNEXTDDS_DIR\bin\rtipkginstall.bat" $rti_security_host_params
	cmd.exe /c "$Env:CONNEXTDDS_DIR\bin\rtipkginstall.bat" $rti_security_target_params
}
