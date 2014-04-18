<?php 
require_once( 'includes/header.php' );
require_once( 'includes/config.php' );

function get_parameter($name, $format, $default) {
	if (isset($_POST[$name])) {
		$val = $_POST[$name];
        } else if (isset($_GET[$name])) {
		$val = $_GET[$name];
        } else {
		$val = $default;
	}
	if (($val != "") && (! preg_match($format, $val))) {
		echo "Erreur interne: ". $val . "<br/>\n";
		require_once( 'includes/footer.php' );
		exit(0);
        } else {
		return $val;
        }
}

$dep = get_parameter("dep", "/^([09][0-9][0-9AB])?$/", "");
$ville = get_parameter("ville", "/^[A-Z0-9][A-Z0-9][0-9][0-9][0-9][-a-zA-Z0-9_ '()]*$/", "");
$type = get_parameter("type", "/^(bati$)|(bati_seul$)|(adresses$)/", "bati");
$command = "";

?>
<div id="conditions-utilisation">
<p>
Ce service et les données du cadastre disponibles ici sont exclusivement réservés à l'usage des contributeurs OpenStreetMap. <a href="http://wiki.openstreetmap.org/wiki/Cadastre_Fran%C3%A7ais/Conditions_d%27utilisation">En savoir plus</a>
</p>
</div>
<div id='information'>
<?php
if( $dep && $ville && $type )
{
	if( !file_exists( $locks_path . '/' . $dep ) )
	{
		@mkdir( $locks_path );
		mkdir( $locks_path . '/' . $dep );
	}
	if( !file_exists( $logs_path . '/' . $dep ) and $do_we_log )
	{
		@mkdir( $logs_path );
		mkdir( $logs_path . '/' . $dep );
	}
	$log_file = $logs_path . '/' . $dep . '/' . $dep . '-' . $ville . '-' . $type . '.log';
	$lock_file = $locks_path . '/' . $dep . '/' . $dep . '-' . $ville . '-' . $type . '.lock';
	if( file_exists( $lock_file ) && ((time() - filemtime ( $lock_file )) < 2*60*60)) {
		echo 'Import en cours';
	}
	else
	{
		register_shutdown_function ( unlink, $lock_file );
		if( touch( $lock_file ) )
		{
		    chmod( $lock_file, 0664);
			if ($do_we_log)
			{
				$log = fopen( $logs_path . '/log.txt', 'a+' );
				fwrite( $log, date( 'd-m-Y H:i:s' ) . ' ' . $_SERVER['REMOTE_ADDR'] . ' : ' . $dep . ' ' . $ville . "" . $type . ";\n" );
				fclose( $log );
				if ($type == "adresses") { 
					$log_cmd="2>&1 |tee \"$log_file\"";
				} else {
					$log_cmd="> \"$log_file\" 2>&1";
				}
			}
			else
			{
				if ($type == "adresses") { 
					$log_cmd="2>&1";
				} else {
					$log_cmd="> /dev/null 2>&1";
				}
			}
			$v = explode( '-', $ville, 2 );
			if ($type == "adresses") { 
				$command = sprintf( "cd %s && ./import-adresses.sh %s %s \"%s\" $log_cmd", $bin_path, $dep, $v[0], trim( $v[1] ));
			} else {
			    $command = sprintf( "cd %s && ./import-ville.sh %s %s \"%s\" $type $log_cmd", $bin_path, $dep, $v[0], trim( $v[1] ));
				exec( $command );
				echo 'Import ok. Acc&egrave;s <a href="data/' . $dep . '">aux fichiers</a> - <a href="data/' . $dep . '/' . $v[0] . '-' . trim( $v[1] ) . '.tar.bz2">&agrave; l\'archive</a>';
				$command = '';
			}
		}
		else
			echo 'Something went wrong';
	}
}
?>
</div>

<form name='form-dep' action='' method='POST'>
	<fieldset id='fdep'>
		<legend>Choix du d&eacute;partement</legend>
		<label>D&eacute;partement&nbsp;:</label>
		<select name='dep' id='dep' onChange='javascript:getDepartement();'>
			<option></option>
<?php
if( $handle = opendir( $data_path ) )
{
	foreach( $dep_array as $d )
	{
		if( !isset( $d['name'] ) )
			$d['name'] = $d['id'];
		echo "\t\t\t" . '<option value="' . $d['id'] . '"';
		if( $dep == $d['id'] )
			echo ' selected="selected"';
		echo '>' . $d['name'] . "</option>\n";
	}
	closedir( $handle );
}
else
	echo 'No data';
?>
		</select>
		<input value="Recherche" type="text" id="recherche_dep" name="recherche_dep" maxlength="40" size="20" onfocus="javascript:if(this.value == 'Recherche') this.value='';" onchange="javascript:filter_dep();" onkeyup="javascript:filter_dep();" onpaste="javascript:filter_dep();" onmouseup="javascript:filter_dep();"/>
	</fieldset>
	<fieldset id='fville'>
		<legend>Choix de la commune</legend>
		<img src='images/throbber_16.gif' style='display:none;' alt='pending' id='throbber_ville' />
		<select id='ville' name='ville'>
<?php 
if ($dep) {
  include("getDepartement.php");
}
?>
		</select>
		<input value="Recherche" type="text" id="recherche_ville" name="recherche_ville" maxlength="60" size="20" onfocus="javascript:if(this.value == 'Recherche') this.value='';" onchange="javascript:filter_ville();" onkeyup="javascript:filter_ville();" onpaste="javascript:filter_ville();" onmouseup="javascript:filter_ville();"/>

		<br />
		<p style='font-size:small;'><img src='images/info.png' alt='!' style='vertical-align:sub;' />&nbsp;Le code indiqué à coté du nom de la commune est son <a href='http://fr.wikipedia.org/wiki/Code_Insee#Identification_des_collectivit.C3.A9s_locales_.28et_autres_donn.C3.A9es_g.C3.A9ographiques.29'>code INSEE</a>, pas son code postal</p>
		<p style='font-size:small;'>Seules les communes existant au format vecteur au cadastre sont listées</p>
	</fieldset>
	<fieldset id='ftype'>
		<legend>Choix du type de données</legend>
<?php
$bati_checked = ($type=="bati") ? "checked" : "";
$bati_seul_checked = ($type=="bati_seul") ? "checked" : "";
$adresses_checked = ($type=="adresses") ? "checked" : "";
?>
		<input type="radio" name="type" value="adresses" <?php echo $adresses_checked;?>>Adresses</input><br/>
		<input type="radio" name="type" value="bati" <?php echo $bati_checked;?>>Bâti &amp; Limites</input><br/>
		<input type="radio" name="type" value="bati_seul" <?php echo $bati_seul_checked;?>>Bâti seul <small>(pour les villes où l'extraction Bâti &amp; Limites échoue)</small></input><br/>
	</fieldset>
	<fieldset id='mise_en_garde'>
		<legend>Mise en garde</legend>
		<p>
		L'intégration de données <i><u>bâtiments</u></i> en provenance du cadastre n'est pas triviale, si vous ne venez pas de <a href='http://wiki.openstreetmap.org/wiki/WikiProject_France/Cadastre/Import_semi-automatique_des_b%C3%A2timents'>la page suivante</a>, il est vivement recommandé d'aller la lire !
		<br/>
		Pour les <i><u>limites</u></i> de communes, ce n'est pas trivial non plus et la <a href='http://wiki.openstreetmap.org/wiki/WikiProject_France/Limites_administratives/Tracer_les_limites_administratives'>documentation est ici.</a>
		<br/>
		Pour l'intégration des données <i><u>adresses</u></i>, <a href='http://wiki.openstreetmap.org/wiki/WikiProject_France/Cadastre/Import_semi-automatique_des_adresses'>il faut lire cette page</a>.
		</p>
	</fieldset>
	<div>
		<input type='submit' value='Générer' />
	</div>
</form>
<p>
Note: Vous pensez avoir trouvé un bug ? <a href='http://trac.openstreetmap.fr/newticket?component=export%20cadastre&owner=vdct&cc=tyndare'>Vous pouvez le signaler ici (composant export cadastre)</a>
</p>
<script type='text/javascript'>
<?php
if ($ville) {
	echo "\tdocument.getElementById( 'ville' ).focus();\n";
} else {
	echo "\tdocument.getElementById( 'dep' ).focus();\n";
}
?>
</script>
<?php
if ($command) {
    class ProcessLineReader {
      private $resource;
      private $pipes;
      private $state;
      function __construct($cmd) {
        $descriptorspec    = array(
          0 => array('pipe', 'r'),
          1 => array('pipe', 'w'),
          2 => array('pipe', 'w')
        );
        $this->resource = proc_open($cmd, $descriptorspec, $this->pipes);
        $state = 1;
        fclose($this->pipes[0]);
      }
      function readstd() {
        if ($this->resource !== FALSE) {
          return fgets($this->pipes[1]);
        } else {
          return $FALSE;
        }
      }
      function readerror() {
        if ($this->resource !== FALSE) {
          return fgets($this->pipes[2]);
        } else {
          return $FALSE;
        }
      }
      function close() {
              fclose($this->pipes[1]);
              fclose($this->pipes[2]);
              proc_close($this->resource);
              $this->resource = FALSE;
      }
      function print_error_and_close() {
        while($line = $this->readerror()) {
          print "<pre>" . $line . "</pre>";
        }
        $this->close();
      }
    }
    print "<pre>";
    $process = new ProcessLineReader("$command");
    ob_end_flush();
    flush();
    while($line = $process->readstd()) {
      print $line;
      flush();
    }
    $process->print_error_and_close();

    $associatedStreet_files = array (
        "Mix en façade proche ou point isolé" => "/data/$dep/$ville-adresses-associatedStreet_mix_en_facade_ou_isole.zip",
        "Toujours en façade de bâtiment" => "/data/$dep/$ville-adresses-associatedStreet_point_sur_batiment.zip",
        "Toujours comme attribut de bâtiment" => "/data/$dep/$ville-adresses-associatedStreet_tag_sur_batiment.zip",
        "Toujours comme point isolés" => "/data/$dep/$ville-adresses-associatedStreet_sans_batiment.zip",
    );
    $addrstreet_files = array();
    foreach($associatedStreet_files as $key => $val) {
        $addrstreet_files[$key] = str_replace("associatedStreet","addrstreet",$associatedStreet_files[$key]);
    }
    print "</pre>\n";
    print "<fieldset>\n";
    echo "<legend>Résultat avec tag addr:street:</legend>\n";
    echo "<table class=\"result\">\n";
    foreach($addrstreet_files as $key => $val) {
        echo "<tr><td>$key: </td><td><a href='$val'>" . basename($val) . "</a></td></tr>\n";
    }
    echo "</table>\n";
    print "</fieldset>\n";
    print "<fieldset>\n";
    echo "<legend>Résultat avec relation associatedStreet:</legend>\n";
    echo "<table class=\"result\">\n";
    foreach($associatedStreet_files as $key => $val) {
        echo "<tr><td>$key: </td><td><a href='$val'>" . basename($val) . "</a></td></tr>\n";
    }
    echo "</table>\n";
    print "</fieldset>\n";
    ?>
    <script type='text/javascript'>
    	document.getElementById('information').innerHTML = 'Import ok. Acc&egrave;s <a href="/data/<?php echo $dep;?>">aux fichiers</a>';
    </script>
    <?php
}
require_once( 'includes/footer.php' );
