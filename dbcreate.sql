CREATE TABLE jmeter.jmeter (
	id INT(11) auto_increment NOT NULL,
	app_name varchar(50) NOT NULL,
	files_path varchar(200) NOT NULL,
	jmx VARCHAR(200) NOT NULL,
	properties varchar(200) NULL,
	otherfiles varchar(200) NULL,
	message varchar(300) NULL,
	init_datetime DATETIME NULL,
	now BINARY NOT NULL,
	createdate DATE NOT NULL,
	hostname varchar(50) NULL,
	estate ENUM('pendiente','cancelado','procesando','error','ok','procesado','tomado') NOT NULL,
	duration INT NULL,
	start_datetime DATETIME NULL,
	CONSTRAINT jmeter_PK PRIMARY KEY (id)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;


DROP TABLE jmeter.jmeter ;
//revisar mañana agregar el hostname para el que procesa

CREATE TABLE jmeter.jmeter (
	estado ENUM NULL
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;
		
