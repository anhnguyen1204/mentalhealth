const path = require('path');
const express = require('express');
const session = require('express-session');
const cookieParser = require('cookie-parser');
const multer = require('multer');
const { PrismaClient } = require('@prisma/client');
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

const prisma = new PrismaClient();
const app = express();
const PORT = process.env.PORT || 3000;

// Storage for file uploads
const upload = multer({ dest: path.join(__dirname, '..', 'uploads') });
app.set('upload', upload);
app.set('prisma', prisma);

// View engine
app.set('views', path.join(__dirname, '..', 'views'));
app.set('view engine', 'ejs');

// Middlewares
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(cookieParser());
app.use(session({
	secret: process.env.SESSION_SECRET || 'dev_secret',
	resave: false,
	saveUninitialized: false,
	cookie: { maxAge: 1000 * 60 * 60 * 4 }
}));

// Static
app.use('/public', express.static(path.join(__dirname, '..', 'public')));
app.use('/uploads', express.static(path.join(__dirname, '..', 'uploads')));

// Auth helpers
app.use((req, res, next) => {
	res.locals.currentUser = req.session.user || null;
	next();
});

// Routers
const authRouter = require('../routes/auth');
const lessonRouter = require('../routes/lessons');
const exerciseRouter = require('../routes/exercises');
const teacherRouter = require('../routes/teacher');

app.use('/', authRouter);
app.use('/lessons', lessonRouter);
app.use('/exercises', exerciseRouter);
app.use('/teacher', teacherRouter);

app.get('/', async (req, res) => {
	const lessons = await prisma.lesson.findMany({
		orderBy: { createdAt: 'desc' },
		include: { createdBy: true }
	});
	res.render('lessons/index', { lessons });
});

// Error handler
app.use((err, req, res, next) => {
	console.error(err);
	res.status(500).send('Internal Server Error');
});

app.listen(PORT, () => {
	console.log(`Server running on http://localhost:${PORT}`);
});